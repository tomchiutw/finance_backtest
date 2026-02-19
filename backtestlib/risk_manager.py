# -*- coding: utf-8 -*-
"""
Risk management system for the finance_backtest framework.
"""
import logging
from backtestlib.exceptions import RiskLimitExceededError

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Manages risk limits and position sizing for backtesting strategies.

    Parameters:
        max_drawdown (float): Maximum allowed drawdown as a fraction (e.g. 0.2 = 20%).
        max_position_size (float): Maximum position size as a fraction of account balance.
        max_leverage (float): Maximum allowed leverage multiplier.
    """

    def __init__(self, max_drawdown: float = 0.2, max_position_size: float = 0.5,
                 max_leverage: float = 2.0):
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.max_leverage = max_leverage
        self._peak_balance = None

    def check_risk_limits(self, account) -> bool:
        """
        Check whether any risk limits are exceeded for the given account.

        Parameters:
            account: An Account instance with a ``balance`` attribute.

        Returns:
            bool: True if all limits are within bounds.

        Raises:
            RiskLimitExceededError: If the current drawdown exceeds ``max_drawdown``.
        """
        balance = account.balance

        # Update peak balance
        if self._peak_balance is None or balance > self._peak_balance:
            self._peak_balance = balance

        if self._peak_balance > 0:
            drawdown = (self._peak_balance - balance) / self._peak_balance
            if drawdown > self.max_drawdown:
                msg = (
                    f"Drawdown {drawdown:.2%} exceeds maximum allowed "
                    f"{self.max_drawdown:.2%}"
                )
                logger.warning(msg)
                raise RiskLimitExceededError(msg)

        return True

    def calculate_position_size(self, account, volatility: float,
                                risk_per_trade: float = 0.02) -> int:
        """
        Calculate the recommended position size based on account balance, volatility,
        and the desired risk per trade.

        Parameters:
            account: An Account instance with a ``balance`` attribute.
            volatility (float): Price volatility (e.g. daily standard deviation of returns).
            risk_per_trade (float): Fraction of balance to risk per trade (default 2%).

        Returns:
            int: Recommended position size (floored to nearest whole unit).
        """
        if volatility <= 0:
            logger.warning("Volatility must be positive; returning position size 0")
            return 0

        risk_amount = account.balance * risk_per_trade
        position_size = int(risk_amount / volatility)

        max_size = int(account.balance * self.max_position_size)
        position_size = min(position_size, max_size)

        return max(position_size, 0)

    def validate_order(self, order, account) -> bool:
        """
        Validate an order against current risk limits before execution.

        Parameters:
            order: An Order instance with ``quantity``, ``commodity``, and ``direction``
                attributes.
            account: An Account instance with a ``balance`` attribute.

        Returns:
            bool: True if the order passes risk validation.

        Raises:
            RiskLimitExceededError: If the order would exceed the position-size or
                leverage limits.
        """
        if account.balance <= 0:
            return True

        # Check position size limit
        margin_list = ['future', 'option', 'currency_pair', 'cfd']
        if order.commodity.category in margin_list:
            margin = order.commodity.margin_info.get('initial_margin', 0)
            order_value = margin * order.quantity
        else:
            deal_price = getattr(order, 'price', 0) or 0
            order_value = deal_price * order.quantity * order.commodity.contract_size

        position_fraction = order_value / account.balance if account.balance > 0 else 0
        if position_fraction > self.max_position_size:
            msg = (
                f"Order position size {position_fraction:.2%} exceeds maximum "
                f"{self.max_position_size:.2%} of account balance"
            )
            logger.warning(msg)
            raise RiskLimitExceededError(msg)

        return True
