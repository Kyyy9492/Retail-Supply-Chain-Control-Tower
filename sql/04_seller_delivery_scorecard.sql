-- 04_seller_delivery_scorecard.sql
-- Purpose: Build seller/supplier performance scorecard.

USE retail_supply_chain;

DROP TABLE IF EXISTS mart_seller_scorecard;
CREATE TABLE mart_seller_scorecard AS
WITH seller_base AS (
    SELECT
        seller_id,
        seller_state,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(price), 2) AS total_revenue,
        ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
        ROUND(AVG(is_late), 4) AS late_rate,
        ROUND(1 - AVG(is_late), 4) AS on_time_rate,
        ROUND(AVG(freight_value), 2) AS avg_freight_value,
        ROUND(AVG(freight_to_price_ratio), 4) AS avg_freight_to_price_ratio,
        ROUND(AVG(review_score), 2) AS avg_review_score
    FROM mart_order_kpis
    WHERE order_status = 'delivered'
    GROUP BY seller_id, seller_state
), normalized AS (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY total_orders) AS volume_score,
        PERCENT_RANK() OVER (ORDER BY avg_review_score) AS review_score_norm,
        1 - PERCENT_RANK() OVER (ORDER BY avg_freight_to_price_ratio) AS freight_efficiency_score
    FROM seller_base
)
SELECT
    *,
    ROUND(
        0.40 * on_time_rate +
        0.30 * COALESCE(review_score_norm, 0) +
        0.20 * COALESCE(freight_efficiency_score, 0) +
        0.10 * COALESCE(volume_score, 0)
    , 4) AS seller_performance_score,
    CASE
        WHEN total_orders >= 50 AND late_rate <= 0.10 THEN 'Core Reliable Seller'
        WHEN total_orders >= 50 AND late_rate > 0.10 THEN 'High Volume Operational Risk'
        WHEN total_orders < 50 AND late_rate <= 0.10 THEN 'Potential Growth Seller'
        ELSE 'Low Volume Risk Seller'
    END AS seller_segment
FROM normalized;
