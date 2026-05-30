-- 03_build_supply_chain_kpis.sql
-- Purpose: Build core supply chain KPI table for dashboarding.

USE retail_supply_chain;

DROP TABLE IF EXISTS mart_order_kpis;
CREATE TABLE mart_order_kpis AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_state,
    c.customer_city,
    oi.seller_id,
    s.seller_state,
    s.seller_city,
    oi.product_id,
    p.product_category,
    o.order_status,
    DATE(o.order_purchase_timestamp) AS order_date,
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
    o.delivery_days,
    o.estimated_delivery_days,
    o.delay_days,
    o.is_late,
    oi.price,
    oi.freight_value,
    oi.freight_to_price_ratio,
    r.review_score,
    pay.payment_value,
    pay.payment_type
FROM clean_orders o
LEFT JOIN clean_order_items oi
    ON o.order_id = oi.order_id
LEFT JOIN stg_customers c
    ON o.customer_id = c.customer_id
LEFT JOIN stg_sellers s
    ON oi.seller_id = s.seller_id
LEFT JOIN clean_products p
    ON oi.product_id = p.product_id
LEFT JOIN stg_reviews r
    ON o.order_id = r.order_id
LEFT JOIN (
    SELECT order_id, SUM(payment_value) AS payment_value, MIN(payment_type) AS payment_type
    FROM stg_payments
    GROUP BY order_id
) pay
    ON o.order_id = pay.order_id;

-- Monthly executive KPI view
DROP VIEW IF EXISTS vw_monthly_supply_chain_kpis;
CREATE VIEW vw_monthly_supply_chain_kpis AS
SELECT
    order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price), 2) AS total_revenue,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(is_late), 4) AS late_delivery_rate,
    ROUND(AVG(freight_value), 2) AS avg_freight_value,
    ROUND(AVG(review_score), 2) AS avg_review_score
FROM mart_order_kpis
WHERE order_status = 'delivered'
GROUP BY order_month;
