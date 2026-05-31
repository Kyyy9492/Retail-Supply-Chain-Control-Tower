from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "raw" / "olist"
OUTPUT_DIR = ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
DOCS_DIR = ROOT / "docs"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", ROOT)
print("Olist data folder:", DATA_DIR)

required_files = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "translation": "product_category_name_translation.csv",
}

missing = [f for f in required_files.values() if not (DATA_DIR / f).exists()]
if missing:
    raise FileNotFoundError(f"Missing files in data/raw/olist: {missing}")

print("Loading CSV files...")

orders = pd.read_csv(DATA_DIR / required_files["orders"])
items = pd.read_csv(DATA_DIR / required_files["items"])
payments = pd.read_csv(DATA_DIR / required_files["payments"])
reviews = pd.read_csv(DATA_DIR / required_files["reviews"])
customers = pd.read_csv(DATA_DIR / required_files["customers"])
sellers = pd.read_csv(DATA_DIR / required_files["sellers"])
products = pd.read_csv(DATA_DIR / required_files["products"])
translation = pd.read_csv(DATA_DIR / required_files["translation"])

print("Raw table shapes:")
for name, df in {
    "orders": orders,
    "items": items,
    "payments": payments,
    "reviews": reviews,
    "customers": customers,
    "sellers": sellers,
    "products": products,
    "translation": translation,
}.items():
    print(f"{name}: {df.shape}")

# -----------------------------
# 1. Clean dates
# -----------------------------
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# -----------------------------
# 2. Build order-level table
# -----------------------------
item_agg = (
    items.groupby("order_id")
    .agg(
        item_count=("order_item_id", "count"),
        seller_count=("seller_id", "nunique"),
        total_item_value=("price", "sum"),
        total_freight_value=("freight_value", "sum"),
    )
    .reset_index()
)

payment_agg = (
    payments.groupby("order_id")
    .agg(
        total_payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "mean"),
    )
    .reset_index()
)

review_agg = (
    reviews.groupby("order_id")
    .agg(
        avg_review_score=("review_score", "mean"),
        review_count=("review_id", "count"),
    )
    .reset_index()
)

order_kpi = (
    orders.merge(customers, on="customer_id", how="left")
    .merge(item_agg, on="order_id", how="left")
    .merge(payment_agg, on="order_id", how="left")
    .merge(review_agg, on="order_id", how="left")
)

order_kpi["delivery_days"] = (
    order_kpi["order_delivered_customer_date"] - order_kpi["order_purchase_timestamp"]
).dt.days

order_kpi["estimated_delivery_days"] = (
    order_kpi["order_estimated_delivery_date"] - order_kpi["order_purchase_timestamp"]
).dt.days

order_kpi["delay_days"] = (
    order_kpi["order_delivered_customer_date"] - order_kpi["order_estimated_delivery_date"]
).dt.days

order_kpi["is_late"] = np.where(order_kpi["delay_days"] > 0, 1, 0)
order_kpi.loc[order_kpi["order_delivered_customer_date"].isna(), "is_late"] = np.nan

order_kpi["order_month"] = order_kpi["order_purchase_timestamp"].dt.to_period("M").astype(str)
order_kpi["freight_to_item_ratio"] = (
    order_kpi["total_freight_value"] / order_kpi["total_item_value"]
).replace([np.inf, -np.inf], np.nan)

delivered = order_kpi[order_kpi["order_delivered_customer_date"].notna()].copy()

print("\nOrder KPI table:", order_kpi.shape)
print("Delivered orders:", delivered.shape)

# -----------------------------
# 3. Executive KPI summary
# -----------------------------
summary = pd.DataFrame(
    {
        "Metric": [
            "Total Orders",
            "Delivered Orders",
            "Late Delivery Rate",
            "Average Delivery Days",
            "Median Delivery Days",
            "Average Delay Days",
            "Total Item Value",
            "Total Freight Value",
            "Average Freight-to-Item Ratio",
            "Average Review Score",
        ],
        "Value": [
            f"{order_kpi['order_id'].nunique():,}",
            f"{delivered['order_id'].nunique():,}",
            f"{delivered['is_late'].mean():.2%}",
            f"{delivered['delivery_days'].mean():.2f}",
            f"{delivered['delivery_days'].median():.2f}",
            f"{delivered['delay_days'].mean():.2f}",
            f"${order_kpi['total_item_value'].sum():,.2f}",
            f"${order_kpi['total_freight_value'].sum():,.2f}",
            f"{order_kpi['freight_to_item_ratio'].mean():.2%}",
            f"{order_kpi['avg_review_score'].mean():.2f}",
        ],
    }
)

summary.to_markdown(TABLE_DIR / "kpi_summary.md", index=False)
print("\nExecutive KPI Summary:")
print(summary)

# -----------------------------
# 4. Monthly KPI table
# -----------------------------
monthly_kpis = (
    delivered.groupby("order_month")
    .agg(
        orders=("order_id", "nunique"),
        late_delivery_rate=("is_late", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        total_item_value=("total_item_value", "sum"),
        total_freight_value=("total_freight_value", "sum"),
        avg_review_score=("avg_review_score", "mean"),
    )
    .reset_index()
)

monthly_kpis.to_markdown(TABLE_DIR / "monthly_supply_chain_kpis.md", index=False)

# Figure 1: Monthly order volume
plt.figure(figsize=(12, 6))
plt.plot(monthly_kpis["order_month"], monthly_kpis["orders"], marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Order Volume")
plt.xlabel("Order Month")
plt.ylabel("Orders")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "monthly_order_volume.png", dpi=150)
plt.close()

# Figure 2: Monthly late delivery rate
plt.figure(figsize=(12, 6))
plt.plot(monthly_kpis["order_month"], monthly_kpis["late_delivery_rate"], marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Late Delivery Rate")
plt.xlabel("Order Month")
plt.ylabel("Late Delivery Rate")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "monthly_late_delivery_rate.png", dpi=150)
plt.close()

# -----------------------------
# 5. State delivery performance
# -----------------------------
state_kpis = (
    delivered.groupby("customer_state")
    .agg(
        orders=("order_id", "nunique"),
        late_delivery_rate=("is_late", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_review_score=("avg_review_score", "mean"),
    )
    .reset_index()
    .sort_values("late_delivery_rate", ascending=False)
)

state_kpis_filtered = state_kpis[state_kpis["orders"] >= 100].copy()
state_kpis_filtered.to_markdown(TABLE_DIR / "state_delivery_kpis.md", index=False)

top10_states = state_kpis_filtered.head(10)

plt.figure(figsize=(10, 6))
plt.bar(top10_states["customer_state"], top10_states["late_delivery_rate"])
plt.title("Top 10 States by Late Delivery Rate")
plt.xlabel("Customer State")
plt.ylabel("Late Delivery Rate")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "top10_states_late_rate.png", dpi=150)
plt.close()

# -----------------------------
# 6. Seller scorecard
# -----------------------------
seller_base = (
    items.merge(orders, on="order_id", how="left")
    .merge(sellers, on="seller_id", how="left")
    .merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
)

seller_base["order_delivered_customer_date"] = pd.to_datetime(
    seller_base["order_delivered_customer_date"], errors="coerce"
)
seller_base["order_purchase_timestamp"] = pd.to_datetime(
    seller_base["order_purchase_timestamp"], errors="coerce"
)
seller_base["order_estimated_delivery_date"] = pd.to_datetime(
    seller_base["order_estimated_delivery_date"], errors="coerce"
)

seller_base["delivery_days"] = (
    seller_base["order_delivered_customer_date"] - seller_base["order_purchase_timestamp"]
).dt.days

seller_base["delay_days"] = (
    seller_base["order_delivered_customer_date"] - seller_base["order_estimated_delivery_date"]
).dt.days

seller_base["is_late"] = np.where(seller_base["delay_days"] > 0, 1, 0)
seller_base.loc[seller_base["order_delivered_customer_date"].isna(), "is_late"] = np.nan

seller_delivered = seller_base[seller_base["order_delivered_customer_date"].notna()].copy()

seller_scorecard = (
    seller_delivered.groupby(["seller_id", "seller_state"])
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        total_sales=("price", "sum"),
        total_freight=("freight_value", "sum"),
        late_delivery_rate=("is_late", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_review_score=("review_score", "mean"),
    )
    .reset_index()
)

seller_scorecard = seller_scorecard[seller_scorecard["orders"] >= 20].copy()
seller_scorecard["risk_score"] = (
    seller_scorecard["late_delivery_rate"] * np.log1p(seller_scorecard["orders"])
)

seller_scorecard = seller_scorecard.sort_values("risk_score", ascending=False)
seller_scorecard.head(20).to_markdown(TABLE_DIR / "seller_delivery_scorecard_top20.md", index=False)

plt.figure(figsize=(10, 6))
plt.scatter(
    seller_scorecard["orders"],
    seller_scorecard["late_delivery_rate"],
    alpha=0.6,
)
plt.title("Seller Risk Matrix: Volume vs Late Delivery Rate")
plt.xlabel("Seller Order Volume")
plt.ylabel("Late Delivery Rate")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "seller_risk_matrix.png", dpi=150)
plt.close()

# -----------------------------
# 7. Product category delivery KPI
# -----------------------------
products_translated = products.merge(
    translation, on="product_category_name", how="left"
)

category_base = (
    items.merge(orders, on="order_id", how="left")
    .merge(products_translated, on="product_id", how="left")
    .merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
)

category_base["order_delivered_customer_date"] = pd.to_datetime(
    category_base["order_delivered_customer_date"], errors="coerce"
)
category_base["order_purchase_timestamp"] = pd.to_datetime(
    category_base["order_purchase_timestamp"], errors="coerce"
)
category_base["order_estimated_delivery_date"] = pd.to_datetime(
    category_base["order_estimated_delivery_date"], errors="coerce"
)

category_base["delivery_days"] = (
    category_base["order_delivered_customer_date"] - category_base["order_purchase_timestamp"]
).dt.days

category_base["delay_days"] = (
    category_base["order_delivered_customer_date"] - category_base["order_estimated_delivery_date"]
).dt.days

category_base["is_late"] = np.where(category_base["delay_days"] > 0, 1, 0)
category_base.loc[category_base["order_delivered_customer_date"].isna(), "is_late"] = np.nan

category_base["category"] = category_base["product_category_name_english"].fillna(
    category_base["product_category_name"]
)

category_delivered = category_base[category_base["order_delivered_customer_date"].notna()].copy()

category_kpis = (
    category_delivered.groupby("category")
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        total_sales=("price", "sum"),
        total_freight=("freight_value", "sum"),
        late_delivery_rate=("is_late", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        avg_review_score=("review_score", "mean"),
    )
    .reset_index()
)

category_kpis = category_kpis[category_kpis["orders"] >= 100].sort_values(
    "late_delivery_rate", ascending=False
)

category_kpis.to_markdown(TABLE_DIR / "category_delivery_kpis.md", index=False)

# -----------------------------
# 8. Write initial findings doc
# -----------------------------
late_rate = delivered["is_late"].mean()
avg_delivery = delivered["delivery_days"].mean()
avg_review = delivered["avg_review_score"].mean()

worst_state = state_kpis_filtered.iloc[0]["customer_state"]
worst_state_late_rate = state_kpis_filtered.iloc[0]["late_delivery_rate"]

top_seller = seller_scorecard.iloc[0]["seller_id"]
top_seller_late_rate = seller_scorecard.iloc[0]["late_delivery_rate"]
top_seller_orders = seller_scorecard.iloc[0]["orders"]

findings = f"""# Olist Initial Supply Chain Findings

## Executive Summary

This analysis uses the Olist Brazilian E-Commerce dataset to evaluate delivery performance, seller reliability, freight cost, and customer review outcomes.

## Key KPIs

- Total orders analyzed: {order_kpi['order_id'].nunique():,}
- Delivered orders: {delivered['order_id'].nunique():,}
- Overall late delivery rate: {late_rate:.2%}
- Average delivery time: {avg_delivery:.2f} days
- Average review score: {avg_review:.2f}

## Initial Findings

1. The overall late delivery rate is {late_rate:.2%}, which provides a baseline for fulfillment performance.
2. The average delivery time is {avg_delivery:.2f} days across delivered orders.
3. Among states with at least 100 delivered orders, {worst_state} has the highest late delivery rate at {worst_state_late_rate:.2%}.
4. Seller `{top_seller}` appears as a high-priority operational risk seller, with {top_seller_orders:,} delivered orders and a late delivery rate of {top_seller_late_rate:.2%}.
5. Product category and seller-level scorecards can help operations teams prioritize follow-up actions.

## Business Recommendations

- Build a seller monitoring process using volume, late delivery rate, review score, and freight performance.
- Prioritize high-volume sellers with above-average late delivery rates.
- Monitor states and product categories with longer delivery lead times.
- Use this fulfillment analysis as the first layer of the broader supply chain control tower before adding M5 demand forecasting and inventory optimization.

## Generated Outputs

- `outputs/tables/kpi_summary.md`
- `outputs/tables/monthly_supply_chain_kpis.md`
- `outputs/tables/state_delivery_kpis.md`
- `outputs/tables/seller_delivery_scorecard_top20.md`
- `outputs/tables/category_delivery_kpis.md`
- `outputs/figures/monthly_order_volume.png`
- `outputs/figures/monthly_late_delivery_rate.png`
- `outputs/figures/top10_states_late_rate.png`
- `outputs/figures/seller_risk_matrix.png`
"""

(DOCS_DIR / "olist_initial_findings.md").write_text(findings, encoding="utf-8")

# Save order-level processed table without uploading raw data later
processed_dir = OUTPUT_DIR / "processed_sample"
processed_dir.mkdir(parents=True, exist_ok=True)
order_kpi.head(1000).to_csv(processed_dir / "order_kpi_sample.csv", index=False)

print("\nGenerated output files:")
for path in [
    TABLE_DIR / "kpi_summary.md",
    TABLE_DIR / "monthly_supply_chain_kpis.md",
    TABLE_DIR / "state_delivery_kpis.md",
    TABLE_DIR / "seller_delivery_scorecard_top20.md",
    TABLE_DIR / "category_delivery_kpis.md",
    FIGURE_DIR / "monthly_order_volume.png",
    FIGURE_DIR / "monthly_late_delivery_rate.png",
    FIGURE_DIR / "top10_states_late_rate.png",
    FIGURE_DIR / "seller_risk_matrix.png",
    DOCS_DIR / "olist_initial_findings.md",
]:
    print("-", path)

print("\nOlist EDA completed successfully.")