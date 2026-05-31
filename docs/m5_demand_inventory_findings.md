# M5 Demand Forecasting and Inventory Optimization Findings

## Executive Summary

This phase extends the supply chain control tower from fulfillment analytics to demand planning and inventory optimization.  
The analysis uses the M5 Walmart sales dataset and focuses on `CA_1` store and `FOODS` category.

## Scope

- Store analyzed: `CA_1`
- Category analyzed: `FOODS`
- Forecasting sample: Top 20 SKUs by 365-day unit demand
- Inventory segmentation sample: Top 100 SKUs by 365-day unit demand
- Holdout period: 28 days
- Assumed replenishment lead time: 7 days
- Service level assumption: approximately 95%, using z-score 1.65

## Forecasting Results

The project compares simple, interpretable baseline models:

- 7-day moving average
- 28-day moving average
- Weekday average demand

Best model by average WAPE: **Weekday Average Demand**  
Best model WAPE: **31.25%**

This result provides an interpretable demand-planning baseline. Future iterations can improve forecast accuracy by adding feature-based machine learning models such as Random Forest, XGBoost, or LightGBM.

Forecast accuracy table: `outputs/m5_tables/forecast_accuracy.md`

## ABC/XYZ Segmentation

The analysis classifies SKUs by value and demand variability:

- ABC classification is based on cumulative estimated sales value.
- XYZ classification is based on demand coefficient of variation.

Among the top 100 SKUs:

- A-class SKUs: 49
- Z-class volatile SKUs: 17
- AZ high-value volatile SKUs: 5

## Inventory Policy

For each SKU, the script estimates:

- Average daily demand
- Demand standard deviation
- Safety stock
- Reorder point
- Recommended inventory action

Average recommended safety stock: 33.18 units  
Average recommended reorder point: 112.24 units

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
