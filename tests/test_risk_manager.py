# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.risk_manager module.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtestlib.risk_manager import RiskManager
from backtestlib.exceptions import RiskLimitExceededError


@pytest.fixture
def risk_manager():
    return RiskManager(max_drawdown=0.2, max_position_size=0.5, max_leverage=2.0)


@pytest.fixture
def mock_account():
    account = MagicMock()
    account.balance = 100_000
    return account


def test_check_risk_limits_passes_within_drawdown(risk_manager, mock_account):
    mock_account.balance = 100_000
    result = risk_manager.check_risk_limits(mock_account)
    assert result is True


def test_check_risk_limits_raises_on_excessive_drawdown(risk_manager, mock_account):
    mock_account.balance = 100_000
    risk_manager.check_risk_limits(mock_account)  # Set peak
    mock_account.balance = 70_000  # 30% drawdown > 20% limit
    with pytest.raises(RiskLimitExceededError):
        risk_manager.check_risk_limits(mock_account)


def test_check_risk_limits_within_drawdown(risk_manager, mock_account):
    mock_account.balance = 100_000
    risk_manager.check_risk_limits(mock_account)
    mock_account.balance = 85_000  # 15% drawdown < 20% limit
    result = risk_manager.check_risk_limits(mock_account)
    assert result is True


def test_calculate_position_size_returns_int(risk_manager, mock_account):
    size = risk_manager.calculate_position_size(mock_account, volatility=500.0)
    assert isinstance(size, int)
    assert size >= 0


def test_calculate_position_size_zero_volatility(risk_manager, mock_account):
    size = risk_manager.calculate_position_size(mock_account, volatility=0)
    assert size == 0


def test_calculate_position_size_respects_max_position(risk_manager, mock_account):
    mock_account.balance = 100_000
    # With very low volatility, raw size would be huge; capped by max_position_size
    size = risk_manager.calculate_position_size(mock_account, volatility=0.01)
    max_allowed = int(100_000 * 0.5)
    assert size <= max_allowed


def test_validate_order_passes(risk_manager, mock_account):
    order = MagicMock()
    order.commodity.category = 'stock'
    order.commodity.contract_size = 1
    order.quantity = 10
    order.price = 100
    result = risk_manager.validate_order(order, mock_account)
    assert result is True


def test_validate_order_raises_on_oversized_position(risk_manager, mock_account):
    mock_account.balance = 1_000  # Small balance
    order = MagicMock()
    order.commodity.category = 'stock'
    order.commodity.contract_size = 1
    order.quantity = 10_000
    order.price = 1_000  # Total 10_000_000 >> 50% of 1_000
    with pytest.raises(RiskLimitExceededError):
        risk_manager.validate_order(order, mock_account)
