"""Forecasting helper functions for M5 demand planning."""

from __future__ import annotations

import pandas as pd


def moving_average_forecast(series: pd.Series, window: int = 28, horizon: int = 28) -> pd.Series:
    """Simple baseline forecast using the most recent moving average.

    Parameters
    ----------
    series:
        Historical demand ordered by date.
    window:
        Number of recent days used for the moving average.
    horizon:
        Number of future days to forecast.
    """
    if len(series) == 0:
        raise ValueError("series must contain at least one value")
    value = series.tail(window).mean()
    return pd.Series([value] * horizon)


def create_lag_features(df: pd.DataFrame, group_cols: list[str], target_col: str, lags: list[int]) -> pd.DataFrame:
    """Create lag features for machine-learning forecasting."""
    out = df.copy()
    for lag in lags:
        out[f"lag_{lag}"] = out.groupby(group_cols)[target_col].shift(lag)
    return out


def create_rolling_features(
    df: pd.DataFrame,
    group_cols: list[str],
    target_col: str,
    windows: list[int],
) -> pd.DataFrame:
    """Create rolling mean features by SKU/store group."""
    out = df.copy()
    for window in windows:
        out[f"rolling_mean_{window}"] = (
            out.groupby(group_cols)[target_col]
            .shift(1)
            .rolling(window=window)
            .mean()
            .reset_index(level=group_cols, drop=True)
        )
    return out
