# -*- coding: utf-8 -*-
"""
Data validation utilities for market data quality checks.
"""
import logging
import numpy as np
import pandas as pd
from backtestlib.exceptions import MarketDataError

logger = logging.getLogger(__name__)

# Threshold for detecting extreme price outliers (z-score)
OUTLIER_Z_SCORE_THRESHOLD = 5.0


def validate_market_data(df: pd.DataFrame, symbol: str) -> dict:
    """
    Validate the quality of a market data DataFrame.

    Checks performed:
        - Missing (NaN) values in OHLCV columns
        - Negative or zero prices in Open, High, Low, Close columns
        - Extreme price outliers (z-score > threshold)
        - Date continuity (large gaps between consecutive rows)

    Parameters:
        df (pd.DataFrame): Market data with columns Open, High, Low, Close and a
            DatetimeIndex.
        symbol (str): Ticker symbol used in log/warning messages.

    Returns:
        dict: Validation report with keys ``nan_count``, ``negative_price_count``,
            ``outlier_count``, ``large_gap_count``, and ``is_valid``.

    Raises:
        MarketDataError: If the DataFrame is empty.
    """
    if df is None or df.empty:
        raise MarketDataError(f"Market data for '{symbol}' is empty")

    report = {
        'symbol': symbol,
        'nan_count': 0,
        'negative_price_count': 0,
        'outlier_count': 0,
        'large_gap_count': 0,
        'is_valid': True,
    }

    price_columns = [col for col in ['Open', 'High', 'Low', 'Close'] if col in df.columns]

    # Check for NaN values
    nan_count = df[price_columns].isna().sum().sum()
    report['nan_count'] = int(nan_count)
    if nan_count > 0:
        logger.warning("Symbol '%s': %d NaN value(s) found in price columns", symbol, nan_count)
        report['is_valid'] = False

    # Check for negative or zero prices
    negative_mask = (df[price_columns] <= 0).any(axis=1)
    negative_count = int(negative_mask.sum())
    report['negative_price_count'] = negative_count
    if negative_count > 0:
        logger.warning("Symbol '%s': %d row(s) with non-positive prices detected", symbol, negative_count)
        report['is_valid'] = False

    # Check for extreme outliers using IQR on Close column
    if 'Close' in df.columns:
        close_clean = df['Close'].dropna()
        if len(close_clean) > 3:
            q1 = close_clean.quantile(0.25)
            q3 = close_clean.quantile(0.75)
            iqr = q3 - q1
            median = close_clean.median()
            if iqr > 0:
                lower_fence = q1 - OUTLIER_Z_SCORE_THRESHOLD * iqr
                upper_fence = q3 + OUTLIER_Z_SCORE_THRESHOLD * iqr
            elif median > 0:
                # Fallback: flag values more than OUTLIER_Z_SCORE_THRESHOLD * 100% away from median
                lower_fence = median * (1 - OUTLIER_Z_SCORE_THRESHOLD)
                upper_fence = median * (1 + OUTLIER_Z_SCORE_THRESHOLD)
            else:
                lower_fence = None
                upper_fence = None
            if lower_fence is not None and upper_fence is not None:
                outlier_count = int(((close_clean < lower_fence) | (close_clean > upper_fence)).sum())
                report['outlier_count'] = outlier_count
                if outlier_count > 0:
                    logger.warning(
                        "Symbol '%s': %d outlier(s) detected in Close prices (IQR fence factor %s)",
                        symbol, outlier_count, OUTLIER_Z_SCORE_THRESHOLD
                    )

    # Check for large gaps in DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex) and len(df.index) > 1:
        diffs = df.index.to_series().diff().dropna()
        median_diff = diffs.median()
        large_gap_threshold = median_diff * 10
        large_gaps = int((diffs > large_gap_threshold).sum())
        report['large_gap_count'] = large_gaps
        if large_gaps > 0:
            logger.warning(
                "Symbol '%s': %d large time gap(s) detected in data index",
                symbol, large_gaps
            )

    return report
