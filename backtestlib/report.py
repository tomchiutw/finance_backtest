# -*- coding: utf-8 -*-
"""
Backtest reporting: metrics calculation and HTML report generation.
"""
import logging
import os
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Constants
TRADING_DAYS_PER_YEAR = 252


class BacktestReport:
    """
    Calculates performance metrics and generates reports from backtest results.

    Parameters:
        performance_data (pd.Series or pd.DataFrame): Equity curve / balance series
            indexed by date.
    """

    def __init__(self, performance_data=None):
        self.performance_data = performance_data
        self.metrics = {}

    def calculate_metrics(self, performance_data=None) -> dict:
        """
        Calculate key performance metrics from the equity curve.

        Parameters:
            performance_data (pd.Series, optional): Equity curve. Uses instance data
                if not provided.

        Returns:
            dict: Dictionary of calculated metrics including Sharpe Ratio, Sortino
                Ratio, Calmar Ratio, Max Drawdown, Win Rate, and Profit Factor.
        """
        if performance_data is not None:
            self.performance_data = performance_data

        if self.performance_data is None or len(self.performance_data) < 2:
            logger.warning("Insufficient performance data to calculate metrics")
            return {}

        equity = pd.Series(self.performance_data).dropna()
        returns = equity.pct_change().dropna()

        total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
        n_years = len(equity) / TRADING_DAYS_PER_YEAR
        cagr = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0.0

        # Sharpe Ratio (annualised, assuming 0% risk-free rate)
        mean_return = returns.mean()
        std_return = returns.std()
        sharpe = (mean_return / std_return * np.sqrt(TRADING_DAYS_PER_YEAR)
                  if std_return > 0 else 0.0)

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        sortino = (mean_return / downside_std * np.sqrt(TRADING_DAYS_PER_YEAR)
                   if downside_std > 0 else 0.0)

        # Max Drawdown
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Calmar Ratio
        calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # Win Rate and Profit Factor
        positive = returns[returns > 0]
        negative = returns[returns < 0]
        win_rate = len(positive) / len(returns) if len(returns) > 0 else 0.0
        gross_profit = positive.sum()
        gross_loss = abs(negative.sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        self.metrics = {
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
        }
        return self.metrics

    def generate_html_report(self, output_path: str) -> str:
        """
        Generate a simple HTML report with performance metrics.

        Parameters:
            output_path (str): File path to save the HTML report.

        Returns:
            str: Path to the generated HTML file.
        """
        try:
            from jinja2 import Template
        except ImportError:
            logger.warning("jinja2 not installed; skipping HTML report generation")
            return ''

        if not self.metrics:
            self.calculate_metrics()

        template_str = """<!DOCTYPE html>
<html>
<head><title>Backtest Report</title></head>
<body>
<h1>Backtest Performance Report</h1>
<table border="1" cellpadding="5" cellspacing="0">
  <tr><th>Metric</th><th>Value</th></tr>
  {% for key, value in metrics.items() %}
  <tr>
    <td>{{ key.replace('_', ' ').title() }}</td>
    <td>
      {% if value is not none %}
        {% if key in ['total_return', 'cagr', 'max_drawdown', 'win_rate'] %}
          {{ "%.2f%%"|format(value * 100) }}
        {% else %}
          {{ "%.4f"|format(value) }}
        {% endif %}
      {% else %}
        N/A
      {% endif %}
    </td>
  </tr>
  {% endfor %}
</table>
</body>
</html>"""

        template = Template(template_str)
        html_content = template.render(metrics=self.metrics)

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info("HTML report saved to %s", output_path)
        return output_path

    def plot_equity_curve(self, output_path: str = None):
        """
        Plot the equity curve with drawdown subplot.

        Parameters:
            output_path (str, optional): If provided, save the figure to this path.

        Returns:
            matplotlib.figure.Figure or None: The figure object, or None if data
                is unavailable.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not installed; skipping equity curve plot")
            return None

        if self.performance_data is None:
            logger.warning("No performance data available for plotting")
            return None

        equity = pd.Series(self.performance_data).dropna()
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        ax1.plot(equity.index, equity.values, label='Equity Curve')
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Balance')
        ax1.legend()

        ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.4, color='red')
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown')

        plt.tight_layout()

        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            plt.savefig(output_path)
            logger.info("Equity curve plot saved to %s", output_path)

        return fig

    def plot_trade_analysis(self, returns=None, output_path: str = None):
        """
        Plot trade P&L distribution.

        Parameters:
            returns (pd.Series, optional): Series of trade returns. Uses daily returns
                from equity curve if not provided.
            output_path (str, optional): If provided, save the figure to this path.

        Returns:
            matplotlib.figure.Figure or None
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not installed; skipping trade analysis plot")
            return None

        if returns is None:
            if self.performance_data is None:
                logger.warning("No data available for trade analysis")
                return None
            equity = pd.Series(self.performance_data).dropna()
            returns = equity.pct_change().dropna()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(returns, bins=50, edgecolor='black')
        ax.set_title('Return Distribution')
        ax.set_xlabel('Daily Return')
        ax.set_ylabel('Frequency')

        plt.tight_layout()

        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            plt.savefig(output_path)
            logger.info("Trade analysis plot saved to %s", output_path)

        return fig
