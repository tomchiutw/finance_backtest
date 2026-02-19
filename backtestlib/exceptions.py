# -*- coding: utf-8 -*-
"""
Custom exception classes for the finance_backtest framework.
"""


class MarketDataError(Exception):
    """Raised when there is an error with market data download or processing."""
    pass


class OrderExecutionError(Exception):
    """Raised when an order cannot be executed due to invalid parameters or conditions."""
    pass


class ConfigurationError(Exception):
    """Raised when there is an error loading or validating configuration."""
    pass


class RiskLimitExceededError(Exception):
    """Raised when a risk limit (drawdown, position size, leverage) is exceeded."""
    pass
