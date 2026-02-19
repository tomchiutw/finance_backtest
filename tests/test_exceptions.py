# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.exceptions module.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtestlib.exceptions import (
    MarketDataError,
    OrderExecutionError,
    ConfigurationError,
    RiskLimitExceededError,
)


def test_market_data_error_is_exception():
    with pytest.raises(MarketDataError):
        raise MarketDataError("test error")


def test_order_execution_error_is_exception():
    with pytest.raises(OrderExecutionError):
        raise OrderExecutionError("test error")


def test_configuration_error_is_exception():
    with pytest.raises(ConfigurationError):
        raise ConfigurationError("test error")


def test_risk_limit_exceeded_error_is_exception():
    with pytest.raises(RiskLimitExceededError):
        raise RiskLimitExceededError("test error")


def test_all_are_subclasses_of_exception():
    assert issubclass(MarketDataError, Exception)
    assert issubclass(OrderExecutionError, Exception)
    assert issubclass(ConfigurationError, Exception)
    assert issubclass(RiskLimitExceededError, Exception)
