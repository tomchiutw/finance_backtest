# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.report module.
"""
import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtestlib.report import BacktestReport


@pytest.fixture
def equity_curve():
    """Simple upward-sloping equity curve."""
    dates = pd.date_range('2022-01-01', periods=252, freq='B')
    values = [1_000_000 * (1 + 0.0003) ** i for i in range(252)]
    return pd.Series(values, index=dates)


def test_calculate_metrics_returns_dict(equity_curve):
    report = BacktestReport(equity_curve)
    metrics = report.calculate_metrics()
    assert isinstance(metrics, dict)
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics
    assert 'profit_factor' in metrics


def test_calculate_metrics_total_return_positive(equity_curve):
    report = BacktestReport(equity_curve)
    metrics = report.calculate_metrics()
    assert metrics['total_return'] > 0


def test_calculate_metrics_max_drawdown_non_positive(equity_curve):
    report = BacktestReport(equity_curve)
    metrics = report.calculate_metrics()
    assert metrics['max_drawdown'] <= 0


def test_calculate_metrics_win_rate_between_0_and_1(equity_curve):
    report = BacktestReport(equity_curve)
    metrics = report.calculate_metrics()
    assert 0.0 <= metrics['win_rate'] <= 1.0


def test_calculate_metrics_empty_data():
    report = BacktestReport(pd.Series([], dtype=float))
    metrics = report.calculate_metrics()
    assert metrics == {}


def test_calculate_metrics_single_point():
    report = BacktestReport(pd.Series([1_000_000]))
    metrics = report.calculate_metrics()
    assert metrics == {}


def test_generate_html_report(equity_curve, tmp_path):
    report = BacktestReport(equity_curve)
    report.calculate_metrics()
    output_path = str(tmp_path / "report.html")
    result = report.generate_html_report(output_path)
    assert result == output_path
    assert os.path.exists(output_path)
    content = open(output_path).read()
    assert 'Backtest' in content


def test_plot_equity_curve_returns_figure(equity_curve):
    report = BacktestReport(equity_curve)
    fig = report.plot_equity_curve()
    assert fig is not None


def test_plot_trade_analysis_returns_figure(equity_curve):
    report = BacktestReport(equity_curve)
    fig = report.plot_trade_analysis()
    assert fig is not None
