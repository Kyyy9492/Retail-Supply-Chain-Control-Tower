from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# M5 Demand Forecasting + ABC/XYZ Inventory Segmentation
# Retail Supply Chain Control Tower
# ============================================================

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "raw" / "m5"
OUTPUT_DIR = ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "m5_tables"
FIGURE_DIR = OUTPUT_DIR / "m5_figures"
DOCS_DIR = ROOT / "docs"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", ROOT)
print("M5 data folder:", DATA_DIR)

SALES_FILE = DATA_DIR / "sales_train_validation.csv"
CALENDAR_FILE = DATA_DIR / "calendar.csv"
PRICE_FILE = DATA_DIR / "sell_prices.csv"

required = [SALES_FILE, CALENDAR_FILE, PRICE_FILE]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise FileNotFoundError(f"Missing required M5 files: {missing}")

# -----------------------------
# 1. Load M5 data
# -----------------------------
print("\nLoading M5 sales data...")
sales = pd.read_csv(SALES_FILE)
calendar = pd.read_csv(CALENDAR_FILE)
prices = pd.read_csv(PRICE_FILE)

print("sales:", sales.shape)
print("calendar:", calendar.shape)
print("prices:", prices.shape)

id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
day_cols = [c for c in sales.columns if c.startswith("d_")]

# Use a manageable but meaningful subset for portfolio analysis
TARGET_STORE = "CA_1"
TARGET_CATEGORY = "FOODS"
HISTORY_DAYS = 365
TOP_N_FORECAST = 20
TOP_N_SEGMENT = 100
HOLDOUT_DAYS = 28
LEAD_TIME_DAYS = 7
SERVICE_LEVEL_Z = 1.65  # approx. 95% service level

last_days = day_cols[-HISTORY_DAYS:]

subset = sales[
    (sales["store_id"] == TARGET_STORE) &
    (sales["cat_id"] == TARGET_CATEGORY)
].copy()

if subset.empty:
    raise ValueError(f"No rows found for store={TARGET_STORE}, category={TARGET_CATEGORY}")

subset["total_units_365d"] = subset[last_days].sum(axis=1)
subset = subset.sort_values("total_units_365d", ascending=False)

top_forecast = subset.head(TOP_N_FORECAST).copy()
top_segment = subset.head(TOP_N_SEGMENT).copy()

print(f"\nSelected subset: store={TARGET_STORE}, category={TARGET_CATEGORY}")
print("Rows in subset:", subset.shape[0])
print("Top SKUs for forecasting:", top_forecast.shape[0])
print("Top SKUs for segmentation:", top_segment.shape[0])

# -----------------------------
# 2. Build long daily demand table for top forecast SKUs
# -----------------------------
long_top = top_forecast[id_cols + last_days].melt(
    id_vars=id_cols,
    value_vars=last_days,
    var_name="d",
    value_name="units"
)

# Calendar mapping
calendar_small = calendar[["d", "date", "wm_yr_wk", "weekday", "month", "year"]].copy()
calendar_small["date"] = pd.to_datetime(calendar_small["date"], errors="coerce")

long_top = long_top.merge(calendar_small, on="d", how="left")
long_top = long_top.sort_values(["id", "date"])

daily_total = (
    long_top.groupby("date", as_index=False)
    .agg(units=("units", "sum"))
)

# Figure: Daily demand trend
plt.figure(figsize=(12, 6))
plt.plot(daily_total["date"], daily_total["units"])
plt.title(f"Daily Demand Trend - {TARGET_STORE} {TARGET_CATEGORY} Top {TOP_N_FORECAST} SKUs")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIGURE_DIR / "daily_demand_trend.png", dpi=150)
plt.close()

# -----------------------------
# 3. Forecasting models
# -----------------------------
def wape(actual, forecast):
    actual = np.asarray(actual)
    forecast = np.asarray(forecast)
    denom = np.sum(np.abs(actual))
    if denom == 0:
        return np.nan
    return np.sum(np.abs(actual - forecast)) / denom

def mae(actual, forecast):
    actual = np.asarray(actual)
    forecast = np.asarray(forecast)
    return np.mean(np.abs(actual - forecast))

def rmse(actual, forecast):
    actual = np.asarray(actual)
    forecast = np.asarray(forecast)
    return math.sqrt(np.mean((actual - forecast) ** 2))

forecast_rows = []
forecast_series_rows = []

for sku_id, g in long_top.groupby("id"):
    g = g.sort_values("date").reset_index(drop=True)
    train = g.iloc[:-HOLDOUT_DAYS].copy()
    test = g.iloc[-HOLDOUT_DAYS:].copy()

    if len(train) < 60 or len(test) == 0:
        continue

    actual = test["units"].values

    # Baseline 1: last 7-day moving average
    ma7_value = train["units"].tail(7).mean()
    forecast_ma7 = np.repeat(ma7_value, len(test))

    # Baseline 2: last 28-day moving average
    ma28_value = train["units"].tail(28).mean()
    forecast_ma28 = np.repeat(ma28_value, len(test))

    # Baseline 3: same weekday average from training history
    weekday_avg = train.groupby("weekday")["units"].mean().to_dict()
    overall_avg = train["units"].mean()
    forecast_weekday = test["weekday"].map(weekday_avg).fillna(overall_avg).values

    model_forecasts = {
        "MA7": forecast_ma7,
        "MA28": forecast_ma28,
        "Weekday_Average": forecast_weekday,
    }

    for model_name, fcst in model_forecasts.items():
        forecast_rows.append({
            "sku_id": sku_id,
            "model": model_name,
            "MAE": mae(actual, fcst),
            "RMSE": rmse(actual, fcst),
            "WAPE": wape(actual, fcst),
            "actual_units": actual.sum(),
            "forecast_units": fcst.sum(),
        })

    # Store MA28 forecast for visualization and inventory policy baseline
    for date, actual_units, forecast_units in zip(test["date"], actual, forecast_ma28):
        forecast_series_rows.append({
            "date": date,
            "sku_id": sku_id,
            "actual_units": actual_units,
            "forecast_units": forecast_units,
            "model": "MA28",
        })

forecast_detail = pd.DataFrame(forecast_rows)
forecast_series = pd.DataFrame(forecast_series_rows)

forecast_accuracy = (
    forecast_detail.groupby("model")
    .agg(
        MAE=("MAE", "mean"),
        RMSE=("RMSE", "mean"),
        WAPE=("WAPE", "mean"),
        actual_units=("actual_units", "sum"),
        forecast_units=("forecast_units", "sum"),
    )
    .reset_index()
    .sort_values("WAPE")
)

forecast_accuracy["WAPE"] = forecast_accuracy["WAPE"].round(4)
forecast_accuracy["MAE"] = forecast_accuracy["MAE"].round(2)
forecast_accuracy["RMSE"] = forecast_accuracy["RMSE"].round(2)
forecast_accuracy["actual_units"] = forecast_accuracy["actual_units"].round(0).astype(int)
forecast_accuracy["forecast_units"] = forecast_accuracy["forecast_units"].round(0).astype(int)

forecast_accuracy.to_markdown(TABLE_DIR / "forecast_accuracy.md", index=False)

best_model = forecast_accuracy.iloc[0]["model"]
best_wape = forecast_accuracy.iloc[0]["WAPE"]

print("\nForecast accuracy:")
print(forecast_accuracy)

# Figure: Aggregate forecast vs actual using MA28
forecast_agg = (
    forecast_series.groupby("date", as_index=False)
    .agg(
        actual_units=("actual_units", "sum"),
        forecast_units=("forecast_units", "sum"),
    )
)

plt.figure(figsize=(12, 6))
plt.plot(forecast_agg["date"], forecast_agg["actual_units"], marker="o", label="Actual")
plt.plot(forecast_agg["date"], forecast_agg["forecast_units"], marker="o", label="Forecast")
plt.title(f"Forecast vs Actual - {TARGET_STORE} {TARGET_CATEGORY} Top {TOP_N_FORECAST} SKUs")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(FIGURE_DIR / "forecast_vs_actual.png", dpi=150)
plt.close()

# -----------------------------
# 4. ABC / XYZ segmentation
# -----------------------------
metrics_rows = []
for _, row in top_segment.iterrows():
    demand = row[last_days].values.astype(float)
    total_units = demand.sum()
    avg_daily = demand.mean()
    std_daily = demand.std(ddof=1)
    cv = std_daily / avg_daily if avg_daily > 0 else np.nan

    metrics_rows.append({
        "id": row["id"],
        "item_id": row["item_id"],
        "dept_id": row["dept_id"],
        "cat_id": row["cat_id"],
        "store_id": row["store_id"],
        "state_id": row["state_id"],
        "total_units_365d": total_units,
        "avg_daily_demand": avg_daily,
        "std_daily_demand": std_daily,
        "demand_cv": cv,
    })

sku_metrics = pd.DataFrame(metrics_rows)

# Latest price by item/store
prices_sorted = prices.sort_values(["store_id", "item_id", "wm_yr_wk"])
latest_prices = (
    prices_sorted.groupby(["store_id", "item_id"], as_index=False)
    .tail(1)[["store_id", "item_id", "sell_price"]]
)

sku_metrics = sku_metrics.merge(latest_prices, on=["store_id", "item_id"], how="left")
sku_metrics["sell_price"] = sku_metrics["sell_price"].fillna(0)
sku_metrics["estimated_sales_value"] = sku_metrics["total_units_365d"] * sku_metrics["sell_price"]

sku_metrics = sku_metrics.sort_values("estimated_sales_value", ascending=False).reset_index(drop=True)
total_value = sku_metrics["estimated_sales_value"].sum()
if total_value == 0:
    sku_metrics["value_share"] = sku_metrics["total_units_365d"] / sku_metrics["total_units_365d"].sum()
else:
    sku_metrics["value_share"] = sku_metrics["estimated_sales_value"] / total_value

sku_metrics["cumulative_value_share"] = sku_metrics["value_share"].cumsum()

def abc_class(cum_share):
    if cum_share <= 0.80:
        return "A"
    elif cum_share <= 0.95:
        return "B"
    else:
        return "C"

def xyz_class(cv):
    if pd.isna(cv):
        return "Z"
    if cv <= 0.50:
        return "X"
    elif cv <= 1.00:
        return "Y"
    else:
        return "Z"

sku_metrics["ABC"] = sku_metrics["cumulative_value_share"].apply(abc_class)
sku_metrics["XYZ"] = sku_metrics["demand_cv"].apply(xyz_class)
sku_metrics["ABC_XYZ"] = sku_metrics["ABC"] + sku_metrics["XYZ"]

abc_xyz_summary = (
    sku_metrics.groupby("ABC_XYZ")
    .agg(
        sku_count=("id", "count"),
        total_units_365d=("total_units_365d", "sum"),
        estimated_sales_value=("estimated_sales_value", "sum"),
        avg_daily_demand=("avg_daily_demand", "mean"),
        avg_demand_cv=("demand_cv", "mean"),
    )
    .reset_index()
    .sort_values("ABC_XYZ")
)

abc_xyz_summary["total_units_365d"] = abc_xyz_summary["total_units_365d"].round(0).astype(int)
abc_xyz_summary["estimated_sales_value"] = abc_xyz_summary["estimated_sales_value"].round(2)
abc_xyz_summary["avg_daily_demand"] = abc_xyz_summary["avg_daily_demand"].round(2)
abc_xyz_summary["avg_demand_cv"] = abc_xyz_summary["avg_demand_cv"].round(2)

abc_xyz_summary.to_markdown(TABLE_DIR / "abc_xyz_segmentation_summary.md", index=False)

sku_metrics_export = sku_metrics.copy()
for col in ["total_units_365d", "avg_daily_demand", "std_daily_demand", "demand_cv", "sell_price", "estimated_sales_value", "value_share", "cumulative_value_share"]:
    sku_metrics_export[col] = sku_metrics_export[col].round(4)

sku_metrics_export.head(50).to_markdown(TABLE_DIR / "top50_sku_abc_xyz_details.md", index=False)

# Figure: segment distribution
segment_counts = abc_xyz_summary.sort_values("sku_count", ascending=False)

plt.figure(figsize=(10, 6))
plt.bar(segment_counts["ABC_XYZ"], segment_counts["sku_count"])
plt.title("ABC/XYZ Segment Distribution")
plt.xlabel("ABC/XYZ Segment")
plt.ylabel("SKU Count")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "abc_xyz_segment_distribution.png", dpi=150)
plt.close()

# -----------------------------
# 5. Safety stock and reorder point
# -----------------------------
sku_metrics["lead_time_days"] = LEAD_TIME_DAYS
sku_metrics["service_level_z"] = SERVICE_LEVEL_Z
sku_metrics["safety_stock"] = (
    sku_metrics["service_level_z"] *
    sku_metrics["std_daily_demand"] *
    np.sqrt(sku_metrics["lead_time_days"])
)

sku_metrics["lead_time_demand"] = sku_metrics["avg_daily_demand"] * sku_metrics["lead_time_days"]
sku_metrics["reorder_point"] = sku_metrics["lead_time_demand"] + sku_metrics["safety_stock"]

def inventory_action(row):
    segment = row["ABC_XYZ"]
    if segment.startswith("A") and segment.endswith("Z"):
        return "High value and volatile demand: monitor closely and use higher safety stock."
    if segment.startswith("A") and segment.endswith("X"):
        return "High value and stable demand: use tight replenishment and frequent review."
    if segment.startswith("A"):
        return "High value SKU: prioritize forecast accuracy and availability."
    if segment.startswith("C") and segment.endswith("Z"):
        return "Low value and volatile demand: avoid overstock and review assortment."
    if segment.endswith("Z"):
        return "Volatile demand: use cautious replenishment and monitor stockout risk."
    return "Standard replenishment policy."

sku_metrics["recommended_action"] = sku_metrics.apply(inventory_action, axis=1)

inventory_recommendations = sku_metrics.sort_values(
    ["ABC", "reorder_point"],
    ascending=[True, False]
)[[
    "id", "item_id", "store_id", "ABC", "XYZ", "ABC_XYZ",
    "avg_daily_demand", "std_daily_demand", "demand_cv",
    "lead_time_days", "safety_stock", "reorder_point",
    "recommended_action"
]].head(50).copy()

for col in ["avg_daily_demand", "std_daily_demand", "demand_cv", "safety_stock", "reorder_point"]:
    inventory_recommendations[col] = inventory_recommendations[col].round(2)

inventory_recommendations.to_markdown(TABLE_DIR / "inventory_recommendations_top50.md", index=False)

# Figure: top 20 reorder points
top_reorder = inventory_recommendations.head(20).copy()

plt.figure(figsize=(12, 6))
plt.bar(top_reorder["item_id"], top_reorder["reorder_point"])
plt.title("Top 20 Recommended Reorder Points")
plt.xlabel("Item ID")
plt.ylabel("Reorder Point")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(FIGURE_DIR / "top20_reorder_points.png", dpi=150)
plt.close()

# -----------------------------
# 6. Write findings document
# -----------------------------
a_count = int((sku_metrics["ABC"] == "A").sum())
z_count = int((sku_metrics["XYZ"] == "Z").sum())
az_count = int((sku_metrics["ABC_XYZ"] == "AZ").sum())
avg_reorder_point = sku_metrics["reorder_point"].mean()
avg_safety_stock = sku_metrics["safety_stock"].mean()

findings = f"""# M5 Demand Forecasting and Inventory Optimization Findings

## Executive Summary

This phase extends the supply chain control tower from fulfillment analytics to demand planning and inventory optimization.  
The analysis uses the M5 Walmart sales dataset and focuses on `{TARGET_STORE}` store and `{TARGET_CATEGORY}` category.

## Scope

- Store analyzed: `{TARGET_STORE}`
- Category analyzed: `{TARGET_CATEGORY}`
- Forecasting sample: Top {TOP_N_FORECAST} SKUs by 365-day unit demand
- Inventory segmentation sample: Top {TOP_N_SEGMENT} SKUs by 365-day unit demand
- Holdout period: {HOLDOUT_DAYS} days
- Assumed replenishment lead time: {LEAD_TIME_DAYS} days
- Service level assumption: approximately 95%, using z-score {SERVICE_LEVEL_Z}

## Forecasting Results

The project compares simple, interpretable baseline models:

- 7-day moving average
- 28-day moving average
- Weekday average demand

Best model by average WAPE: **{best_model}**  
Best model WAPE: **{best_wape:.2%}**

Forecast accuracy table: `outputs/m5_tables/forecast_accuracy.md`

## ABC/XYZ Segmentation

The analysis classifies SKUs by value and demand variability:

- ABC classification is based on cumulative estimated sales value.
- XYZ classification is based on demand coefficient of variation.

Among the top {TOP_N_SEGMENT} SKUs:

- A-class SKUs: {a_count}
- Z-class volatile SKUs: {z_count}
- AZ high-value volatile SKUs: {az_count}

## Inventory Policy

For each SKU, the script estimates:

- Average daily demand
- Demand standard deviation
- Safety stock
- Reorder point
- Recommended inventory action

Average recommended safety stock: {avg_safety_stock:.2f} units  
Average recommended reorder point: {avg_reorder_point:.2f} units

## Business Recommendations

1. Use moving-average baselines as an interpretable demand planning benchmark before deploying complex forecasting models.
2. Prioritize A-class SKUs for availability and forecast accuracy.
3. Monitor AZ SKUs closely because they combine high business value with volatile demand.
4. Use reorder point and safety stock estimates to support replenishment decisions.
5. Combine this demand planning module with the Olist fulfillment analytics layer to create a broader supply chain control tower.

## Generated Outputs

- `outputs/m5_tables/forecast_accuracy.md`
- `outputs/m5_tables/abc_xyz_segmentation_summary.md`
- `outputs/m5_tables/top50_sku_abc_xyz_details.md`
- `outputs/m5_tables/inventory_recommendations_top50.md`
- `outputs/m5_figures/daily_demand_trend.png`
- `outputs/m5_figures/forecast_vs_actual.png`
- `outputs/m5_figures/abc_xyz_segment_distribution.png`
- `outputs/m5_figures/top20_reorder_points.png`
"""

(DOCS_DIR / "m5_demand_inventory_findings.md").write_text(findings, encoding="utf-8")

print("\nGenerated M5 output files:")
for path in [
    TABLE_DIR / "forecast_accuracy.md",
    TABLE_DIR / "abc_xyz_segmentation_summary.md",
    TABLE_DIR / "top50_sku_abc_xyz_details.md",
    TABLE_DIR / "inventory_recommendations_top50.md",
    FIGURE_DIR / "daily_demand_trend.png",
    FIGURE_DIR / "forecast_vs_actual.png",
    FIGURE_DIR / "abc_xyz_segment_distribution.png",
    FIGURE_DIR / "top20_reorder_points.png",
    DOCS_DIR / "m5_demand_inventory_findings.md",
]:
    print("-", path)

print("\nM5 demand forecasting and inventory analysis completed successfully.")
