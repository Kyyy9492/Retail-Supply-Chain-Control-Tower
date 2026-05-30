"""Metrics for forecasting and supply chain analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def mae(y_true, y_pred) -> float:
    """Mean absolute error."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred) -> float:
    """Root mean squared error."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def wape(y_true, y_pred) -> float:
    """Weighted absolute percentage error.

    WAPE = sum(abs(actual - forecast)) / sum(actual)
    Useful for demand forecasting because it is stable when individual daily demand values are small.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    denominator = np.sum(np.abs(y_true))
    if denominator == 0:
        return np.nan
    return float(np.sum(np.abs(y_true - y_pred)) / denominator)


def summarize_forecast_metrics(df: pd.DataFrame, actual_col: str, forecast_col: str) -> dict:
    """Return common forecast metrics in one dictionary."""
    return {
        "mae": mae(df[actual_col], df[forecast_col]),
        "rmse": rmse(df[actual_col], df[forecast_col]),
        "wape": wape(df[actual_col], df[forecast_col]),
    }
