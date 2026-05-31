# Retail Supply Chain Control Tower

## Project Overview

This project builds an end-to-end supply chain analytics workflow using two public datasets:

1. **Olist Brazilian E-Commerce Dataset** — used for fulfillment, delivery, freight, seller, customer, and review performance analysis.
2. **M5 Walmart Forecasting Dataset** — used for SKU-level demand forecasting, ABC/XYZ segmentation, safety stock, reorder point, and inventory policy simulation.

The goal is to move beyond simple dashboard reporting and create a realistic analytics workflow that supports operational decision-making.

## Current Progress: Olist Fulfillment & Delivery Analytics

The first phase of this project analyzes the Olist Brazilian E-Commerce dataset to evaluate order fulfillment performance, delivery delays, seller reliability, freight cost, and customer review outcomes.

### Generated Outputs

- Order-level delivery KPI table
- Monthly supply chain KPI summary
- State-level delivery performance analysis
- Seller delivery risk scorecard
- Product category delivery KPI table
- Initial business findings document

### Key Analysis Areas

1. **Delivery Performance**
   - Calculated actual delivery days, estimated delivery days, delay days, and late delivery flags.
   - Measured monthly order volume and late delivery rate trends.

2. **Regional Fulfillment Bottlenecks**
   - Compared late delivery rates across customer states.
   - Identified regions with higher fulfillment risk.

3. **Seller Reliability**
   - Built a seller scorecard using order volume, late delivery rate, delivery time, freight value, and review score.
   - Flagged high-volume sellers with elevated late delivery risk.

4. **Product Category Performance**
   - Compared product categories by order volume, freight cost, delivery delay, and review outcome.

### Sample Visualizations

#### Monthly Order Volume

![Monthly Order Volume](outputs/figures/monthly_order_volume.png)

#### Monthly Late Delivery Rate

![Monthly Late Delivery Rate](outputs/figures/monthly_late_delivery_rate.png)

#### Top 10 States by Late Delivery Rate

![Top 10 States by Late Delivery Rate](outputs/figures/top10_states_late_rate.png)

#### Seller Risk Matrix

![Seller Risk Matrix](outputs/figures/seller_risk_matrix.png)

### Initial Findings

The initial fulfillment analysis is documented here:

[View Olist Initial Findings](docs/olist_initial_findings.md)

## Business Objective

A retail/e-commerce company wants to:

- identify late delivery drivers and fulfillment bottlenecks;
- monitor seller/supplier reliability;
- forecast SKU-level demand;
- classify inventory by value and volatility;
- recommend safety stock and reorder points;
- simulate stockout and overstock tradeoffs under different replenishment policies.

## Tools

- **SQL / MySQL**: data cleaning, star schema, KPI queries
- **Python**: EDA, forecasting, ABC/XYZ segmentation, inventory simulation
- **Power BI / Qlik Sense**: executive dashboard and control-tower reporting
- **GitHub**: project documentation and portfolio presentation

## Repository Structure

```text
retail-supply-chain-control-tower/
├── README.md
├── requirements.txt
├── data_dictionary.md
├── .gitignore
├── config/
│   └── project_config.yaml
├── data/
│   ├── raw/
│   │   ├── olist/
│   │   └── m5/
│   ├── processed/
│   └── sample/
├── sql/
│   ├── 01_create_olist_tables.sql
│   ├── 02_clean_olist_data.sql
│   ├── 03_build_supply_chain_kpis.sql
│   ├── 04_seller_delivery_scorecard.sql
│   └── 05_late_delivery_features.sql
├── notebooks/
│   ├── 01_olist_supply_chain_eda.ipynb
│   ├── 02_m5_demand_forecasting.ipynb
│   ├── 03_abc_xyz_inventory_segmentation.ipynb
│   ├── 04_inventory_policy_simulation.ipynb
│   └── 05_late_delivery_risk_model.ipynb
├── src/
│   ├── data_cleaning.py
│   ├── metrics.py
│   ├── forecasting.py
│   ├── inventory_policy.py
│   └── visualization.py
├── outputs/
│   ├── tables/
│   └── figures/
├── powerbi/
│   └── dashboard_screenshots/
└── docs/
    ├── project_roadmap.md
    ├── business_questions.md
    ├── dashboard_wireframe.md
    └── executive_summary_template.md
```

## Core Workflow

### Phase 1 — Fulfillment Analytics with Olist

1. Import raw CSV files into MySQL.
2. Clean orders, customers, sellers, products, payments, reviews, and order items.
3. Build delivery KPIs:
   - order volume;
   - total revenue;
   - average delivery days;
   - late delivery rate;
   - average freight cost;
   - review score;
   - freight-to-price ratio.
4. Create seller performance scorecards.
5. Identify high-delay regions, categories, and seller groups.

### Phase 2 — Demand Planning with M5

1. Load daily SKU-store sales data.
2. Build weekly/monthly demand tables.
3. Create baseline and machine-learning demand forecasts.
4. Evaluate forecast accuracy using MAE, RMSE, and WAPE.
5. Classify SKUs using ABC/XYZ analysis.
6. Calculate safety stock and reorder points.
7. Simulate inventory outcomes under baseline vs. forecast-based replenishment policies.

### Phase 3 — Dashboard and Business Recommendations

1. Build Power BI dashboard pages:
   - Executive Overview;
   - Delivery Performance;
   - Seller/Supplier Scorecard;
   - Demand Forecasting;
   - Inventory Recommendations.
2. Export dashboard screenshots.
3. Write executive summary with operational recommendations.

## Expected Deliverables

- SQL scripts for schema creation, cleaning, and KPIs
- Python notebooks for EDA, forecasting, segmentation, and simulation
- Power BI dashboard screenshots
- Executive summary
- Final GitHub README with project results and business insights

## Resume Bullet Draft

**Retail Supply Chain Control Tower | SQL, Python, Power BI, Qlik Sense**

- Built an end-to-end supply chain analytics workflow using Olist e-commerce and Walmart M5 sales data to analyze delivery performance, seller reliability, demand patterns, and inventory replenishment strategies.
- Designed SQL fact/dimension tables and KPI queries to track order volume, late delivery rate, freight cost, seller performance, and regional fulfillment bottlenecks.
- Developed Python forecasting, ABC/XYZ segmentation, safety stock, and reorder point modules to classify SKU demand patterns and simulate stockout vs. overstock tradeoffs.
- Created an interactive business intelligence dashboard with executive KPIs, delivery delay analysis, seller scorecards, and inventory recommendations to support operational decision-making.

## Data Notes

Raw data is not included in this repository because of file size and dataset licensing/platform requirements. Download the datasets separately and place them under:

```text
data/raw/olist/
data/raw/m5/
```
