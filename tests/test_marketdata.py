# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.marketdata module.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import backtestlib.marketdata as bm


@pytest.fixture
def market_data():
    """Create a MarketData instance for testing (no file I/O)."""
    return bm.MarketData(
        symbol='TEST',
        category='stock',
        currency='usd',
        contract='default',
        contract_size=1,
    )


def test_check_interval_valid(market_data):
    """Valid intervals should not raise."""
    for interval in ['1d', '1h', '5m']:
        market_data.check_interval(interval)  # should not raise


def test_check_interval_invalid(market_data):
    """Invalid interval should raise ValueError."""
    with pytest.raises(ValueError):
        market_data.check_interval('invalid')


def test_get_marketdata_saved_path_in_list(market_data):
    result = market_data.get_marketdata_saved_path_in_list()
    assert result == ['data', 'stock', 'TEST', 'default']


def test_get_marketdata_file_name(market_data):
    name = market_data.get_marketdata_file_name('1d')
    assert name == 'TEST_default_1d'
    name_with_note = market_data.get_marketdata_file_name('1d', '_adj')
    assert name_with_note == 'TEST_default_1d_adj'


def test_data_dict_initialized_empty(market_data):
    assert market_data.data == {}


def test_download_data_raises_on_empty(market_data):
    """download_data_from_yfinance should raise ValueError if yfinance returns empty data."""
    with patch('yfinance.Ticker') as mock_ticker_cls, \
         patch('yfinance.download', return_value=pd.DataFrame()):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        with pytest.raises(ValueError, match="empty"):
            market_data.download_data_from_yfinance('1d', '2023-01-01', '2023-12-31')


def test_get_data_from_parquet_missing_file(market_data, tmp_path, monkeypatch):
    """get_data_from_parquet should raise ValueError when file does not exist."""
    monkeypatch.setattr('get_base_dir.get_base_dir', lambda: str(tmp_path))
    with pytest.raises(ValueError, match="Parquet file not found"):
        market_data.get_data_from_parquet('1d')


def test_save_and_load_parquet(market_data, tmp_path, monkeypatch):
    """Data saved via save_data_to_parquet can be loaded back."""
    monkeypatch.setattr('get_base_dir.get_base_dir', lambda: str(tmp_path))

    dates = pd.date_range('2023-01-01', periods=5, freq='D')
    df = pd.DataFrame({
        'Open': [100, 101, 102, 103, 104],
        'High': [105, 106, 107, 108, 109],
        'Low':  [95, 96, 97, 98, 99],
        'Close': [102, 103, 104, 105, 106],
        'Volume': [1000, 1100, 1200, 1300, 1400],
    }, index=dates)

    market_data.save_data_to_parquet(df, '1d')
    loaded = market_data.get_data_from_parquet('1d')
    assert len(loaded) == 5
    assert list(loaded.columns) == ['Open', 'High', 'Low', 'Close', 'Volume']
