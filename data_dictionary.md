# Data Dictionary Draft

## Olist Dataset

Expected raw files:

| File | Purpose |
|---|---|
| `olist_orders_dataset.csv` | Order status and order lifecycle timestamps |
| `olist_order_items_dataset.csv` | Order item, seller, price, freight value |
| `olist_customers_dataset.csv` | Customer ID, zip prefix, city, state |
| `olist_sellers_dataset.csv` | Seller ID, zip prefix, city, state |
| `olist_products_dataset.csv` | Product ID, category, dimensions, weight |
| `olist_order_payments_dataset.csv` | Payment type, installments, payment value |
| `olist_order_reviews_dataset.csv` | Review score and review timestamps |
| `olist_geolocation_dataset.csv` | Zip-prefix location data |
| `product_category_name_translation.csv` | Product category English translation |

Key derived fields:

| Field | Definition |
|---|---|
| `delivery_days` | Days from purchase timestamp to customer delivery date |
| `estimated_delivery_days` | Days from purchase timestamp to estimated delivery date |
| `delay_days` | Actual delivered date minus estimated delivery date |
| `is_late` | 1 if `delay_days > 0`, otherwise 0 |
| `freight_to_price_ratio` | Freight value divided by product price |
| `seller_late_rate` | Percentage of seller's delivered orders that were late |
| `customer_region` | Customer state or grouped geographic region |

## M5 Dataset

Expected raw files:

| File | Purpose |
|---|---|
| `sales_train_evaluation.csv` or `sales_train_validation.csv` | Daily item-store sales history |
| `calendar.csv` | Date, event, SNAP, and week information |
| `sell_prices.csv` | Store-item weekly selling price |
| `sample_submission.csv` | Kaggle submission template, optional |

Key derived fields:

| Field | Definition |
|---|---|
| `daily_demand` | Units sold by item-store-date |
| `weekly_demand` | Aggregated demand by item-store-week |
| `avg_daily_demand` | Mean daily demand for each SKU-store |
| `demand_std` | Standard deviation of daily demand |
| `cv` | Coefficient of variation = demand standard deviation / average demand |
| `abc_class` | SKU value class based on cumulative sales/revenue contribution |
| `xyz_class` | SKU volatility class based on CV |
| `safety_stock` | Buffer stock required for service-level protection |
| `reorder_point` | Demand during lead time plus safety stock |
