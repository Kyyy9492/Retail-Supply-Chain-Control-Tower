# Olist Initial Supply Chain Findings

## Executive Summary

This analysis uses the Olist Brazilian E-Commerce dataset to evaluate delivery performance, seller reliability, freight cost, and customer review outcomes.

## Key KPIs

- Total orders analyzed: 99,441
- Delivered orders: 96,476
- Overall late delivery rate: 6.77%
- Average delivery time: 12.09 days
- Average review score: 4.16

## Initial Findings

1. The overall late delivery rate is 6.77%, which provides a baseline for fulfillment performance.
2. The average delivery time is 12.09 days across delivered orders.
3. Among states with at least 100 delivered orders, AL has the highest late delivery rate at 21.41%.
4. Seller `2709af9587499e95e803a6498a5a56e9` appears as a high-priority operational risk seller, with 25 delivered orders and a late delivery rate of 50.00%.
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
