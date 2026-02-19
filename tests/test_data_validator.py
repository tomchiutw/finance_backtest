# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.data_validator module.
"""
import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtestlib.data_validator import validate_market_data
from backtestlib.exceptions import MarketDataError


@pytest.fixture
def valid_df():
    dates = pd.date_range('2023-01-01', periods=10, freq='D')
    return pd.DataFrame({
        'Open':  [100 + i for i in range(10)],
        'High':  [105 + i for i in range(10)],
        'Low':   [95 + i for i in range(10)],
        'Close': [102 + i for i in range(10)],
        'Volume': [1000] * 10,
    }, index=dates)


def test_validate_clean_data_returns_valid(valid_df):
    report = validate_market_data(valid_df, 'TEST')
    assert report['is_valid'] is True
    assert report['nan_count'] == 0
    assert report['negative_price_count'] == 0


def test_validate_empty_df_raises():
    with pytest.raises(MarketDataError):
        validate_market_data(pd.DataFrame(), 'TEST')


def test_validate_none_raises():
    with pytest.raises(MarketDataError):
        validate_market_data(None, 'TEST')


def test_validate_nan_detected(valid_df):
    valid_df.loc[valid_df.index[2], 'Close'] = np.nan
    report = validate_market_data(valid_df, 'TEST')
    assert report['nan_count'] >= 1
    assert report['is_valid'] is False


def test_validate_negative_price_detected(valid_df):
    valid_df.loc[valid_df.index[0], 'Low'] = -5
    report = validate_market_data(valid_df, 'TEST')
    assert report['negative_price_count'] >= 1
    assert report['is_valid'] is False


def test_validate_outlier_detected():
    dates = pd.date_range('2023-01-01', periods=20, freq='D')
    close_values = [100.0] * 20
    close_values[10] = 1_000_000.0  # Extreme outlier (z-score >> threshold)
    df = pd.DataFrame({
        'Open': close_values,
        'High': close_values,
        'Low': close_values,
        'Close': close_values,
    }, index=dates)
    report = validate_market_data(df, 'TEST')
    assert report['outlier_count'] >= 1


def test_validate_report_contains_symbol(valid_df):
    report = validate_market_data(valid_df, 'MYSYMBOL')
    assert report['symbol'] == 'MYSYMBOL'
