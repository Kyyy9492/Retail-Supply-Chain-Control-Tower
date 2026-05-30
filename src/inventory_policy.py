"""Inventory policy calculations: ABC/XYZ, safety stock, reorder point, and simulation."""

from __future__ import annotations

import numpy as np
import pandas as pd

Z_SCORE_BY_SERVICE_LEVEL = {
    0.90: 1.28,
    0.95: 1.65,
    0.99: 2.33,
}


def assign_abc(df: pd.DataFrame, value_col: str, a_cutoff: float = 0.80, b_cutoff: float = 0.95) -> pd.DataFrame:
    """Assign ABC class based on cumulative value contribution."""
    out = df.copy().sort_values(value_col, ascending=False)
    total_value = out[value_col].sum()
    out["value_share"] = out[value_col] / total_value if total_value else 0
    out["cumulative_value_share"] = out["value_share"].cumsum()
    out["abc_class"] = np.select(
        [out["cumulative_value_share"] <= a_cutoff, out["cumulative_value_share"] <= b_cutoff],
        ["A", "B"],
        default="C",
    )
    return out


def assign_xyz(df: pd.DataFrame, mean_col: str, std_col: str, x_cutoff: float = 0.50, y_cutoff: float = 1.00) -> pd.DataFrame:
    """Assign XYZ class based on demand coefficient of variation."""
    out = df.copy()
    out["cv"] = out[std_col] / out[mean_col].replace({0: np.nan})
    out["xyz_class"] = np.select(
        [out["cv"] <= x_cutoff, out["cv"] <= y_cutoff],
        ["X", "Y"],
        default="Z",
    )
    return out


def safety_stock(demand_std: float, lead_time_days: int, service_level: float = 0.95) -> float:
    """Calculate safety stock using demand variability during lead time."""
    z = Z_SCORE_BY_SERVICE_LEVEL.get(service_level, 1.65)
    return float(z * demand_std * np.sqrt(lead_time_days))


def reorder_point(avg_daily_demand: float, demand_std: float, lead_time_days: int, service_level: float = 0.95) -> float:
    """Calculate reorder point = demand during lead time + safety stock."""
    return float(avg_daily_demand * lead_time_days + safety_stock(demand_std, lead_time_days, service_level))


def simulate_inventory_policy(
    demand: pd.Series,
    reorder_point_value: float,
    order_quantity: float,
    initial_inventory: float | None = None,
) -> pd.DataFrame:
    """Simple reorder-point inventory simulation.

    This is intentionally simple for portfolio readability. It can be expanded later.
    """
    if initial_inventory is None:
        initial_inventory = reorder_point_value + order_quantity

    records = []
    inventory = float(initial_inventory)

    for date, daily_demand in demand.items():
        beginning_inventory = inventory
        fulfilled = min(inventory, daily_demand)
        stockout_units = max(daily_demand - inventory, 0)
        inventory = max(inventory - daily_demand, 0)

        order_placed = 0
        if inventory <= reorder_point_value:
            inventory += order_quantity
            order_placed = 1

        records.append({
            "date": date,
            "beginning_inventory": beginning_inventory,
            "daily_demand": daily_demand,
            "fulfilled_units": fulfilled,
            "stockout_units": stockout_units,
            "ending_inventory": inventory,
            "order_placed": order_placed,
        })

    return pd.DataFrame(records)
