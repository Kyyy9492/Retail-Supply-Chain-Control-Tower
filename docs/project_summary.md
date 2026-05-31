# Project Summary: Retail Supply Chain Control Tower

## Objective

Built an end-to-end supply chain analytics workflow to analyze fulfillment performance, forecast SKU-level demand, and recommend inventory replenishment actions.

## Data

- Olist Brazilian E-Commerce dataset: 99K+ e-commerce orders
- M5 Walmart Forecasting dataset: SKU-level daily sales data

## Methods

- Delivery KPI analysis
- Seller risk scorecard
- Regional fulfillment bottleneck analysis
- Demand forecasting baseline models
- MAE, RMSE, and WAPE model evaluation
- ABC/XYZ inventory segmentation
- Safety stock and reorder point estimation

## Key Results

- Analyzed 99,441 orders and 96,476 delivered orders.
- Measured an overall late delivery rate of 6.77%.
- Built seller and state-level delivery performance scorecards.
- Identified Weekday Average Demand as the best baseline forecasting model with 31.25% WAPE.
- Classified top 100 SKUs into ABC/XYZ inventory segments.
- Identified 49 A-class SKUs, 17 volatile Z-class SKUs, and 5 high-value volatile AZ SKUs.
- Estimated average recommended safety stock of 33.18 units and average reorder point of 112.24 units.

## Business Value

This project demonstrates how supply chain teams can combine fulfillment analytics, demand forecasting, and inventory policy recommendations to support operational decision-making. The workflow connects delivery performance monitoring, SKU-level demand planning, and replenishment recommendations into one portfolio-ready supply chain control tower.

## Tools

Python, pandas, numpy, matplotlib, SQL, forecasting metrics, ABC/XYZ segmentation, safety stock, reorder point analysis, GitHub
