"""Data loading and cleaning helper functions."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    """Read a CSV file with a clear error message."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}. Check that raw data is placed in the correct folder.")
    return pd.read_csv(path, **kwargs)


def optimize_m5_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Light memory optimization for M5-style wide sales data."""
    out = df.copy()
    for col in out.columns:
        if col.startswith("d_"):
            out[col] = pd.to_numeric(out[col], downcast="integer")
    return out


def melt_m5_sales(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Convert M5 wide daily sales table into long format.

    Expected identifier columns include item_id, dept_id, cat_id, store_id, state_id.
    """
    id_cols = [col for col in ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"] if col in sales_df.columns]
    day_cols = [col for col in sales_df.columns if col.startswith("d_")]
    long_df = sales_df.melt(id_vars=id_cols, value_vars=day_cols, var_name="d", value_name="daily_demand")
    return long_df
