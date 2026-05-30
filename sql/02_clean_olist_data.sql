-- 02_clean_olist_data.sql
-- Purpose: Create cleaned analytical tables and derived delivery fields.

USE retail_supply_chain;

DROP TABLE IF EXISTS clean_orders;
CREATE TABLE clean_orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    DATEDIFF(order_delivered_customer_date, order_purchase_timestamp) AS delivery_days,
    DATEDIFF(order_estimated_delivery_date, order_purchase_timestamp) AS estimated_delivery_days,
    DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date) AS delay_days,
    CASE
        WHEN order_delivered_customer_date IS NULL THEN NULL
        WHEN DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date) > 0 THEN 1
        ELSE 0
    END AS is_late
FROM stg_orders;

DROP TABLE IF EXISTS clean_order_items;
CREATE TABLE clean_order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    CASE WHEN price > 0 THEN freight_value / price ELSE NULL END AS freight_to_price_ratio
FROM stg_order_items;

DROP TABLE IF EXISTS clean_products;
CREATE TABLE clean_products AS
SELECT
    p.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS product_category,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    (p.product_length_cm * p.product_height_cm * p.product_width_cm) AS product_volume_cm3
FROM stg_products p
LEFT JOIN stg_category_translation t
    ON p.product_category_name = t.product_category_name;
