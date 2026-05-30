-- 05_late_delivery_features.sql
-- Purpose: Create a modeling table for late delivery prediction.

USE retail_supply_chain;

DROP TABLE IF EXISTS model_late_delivery_features;
CREATE TABLE model_late_delivery_features AS
WITH seller_history AS (
    SELECT
        seller_id,
        AVG(is_late) AS seller_historical_late_rate,
        AVG(delivery_days) AS seller_avg_delivery_days,
        COUNT(DISTINCT order_id) AS seller_order_count
    FROM mart_order_kpis
    WHERE order_status = 'delivered'
    GROUP BY seller_id
), category_history AS (
    SELECT
        product_category,
        AVG(is_late) AS category_historical_late_rate,
        AVG(delivery_days) AS category_avg_delivery_days
    FROM mart_order_kpis
    WHERE order_status = 'delivered'
    GROUP BY product_category
)
SELECT
    k.order_id,
    k.order_date,
    MONTH(k.order_date) AS order_month_num,
    k.customer_state,
    k.seller_state,
    k.product_category,
    k.price,
    k.freight_value,
    k.freight_to_price_ratio,
    k.review_score,
    sh.seller_historical_late_rate,
    sh.seller_avg_delivery_days,
    sh.seller_order_count,
    ch.category_historical_late_rate,
    ch.category_avg_delivery_days,
    k.is_late
FROM mart_order_kpis k
LEFT JOIN seller_history sh
    ON k.seller_id = sh.seller_id
LEFT JOIN category_history ch
    ON k.product_category = ch.product_category
WHERE k.order_status = 'delivered'
  AND k.is_late IS NOT NULL;
