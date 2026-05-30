-- 01_create_olist_tables.sql
-- Purpose: Create staging tables for Olist raw CSV files.
-- Database suggestion: retail_supply_chain

CREATE DATABASE IF NOT EXISTS retail_supply_chain;
USE retail_supply_chain;

DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_status VARCHAR(30),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME
);

DROP TABLE IF EXISTS stg_order_items;
CREATE TABLE stg_order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME,
    price DECIMAL(12,2),
    freight_value DECIMAL(12,2)
);

DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    customer_id VARCHAR(50),
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

DROP TABLE IF EXISTS stg_sellers;
CREATE TABLE stg_sellers (
    seller_id VARCHAR(50),
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products (
    product_id VARCHAR(50),
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

DROP TABLE IF EXISTS stg_payments;
CREATE TABLE stg_payments (
    order_id VARCHAR(50),
    payment_sequential INT,
    payment_type VARCHAR(30),
    payment_installments INT,
    payment_value DECIMAL(12,2)
);

DROP TABLE IF EXISTS stg_reviews;
CREATE TABLE stg_reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50),
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME
);

DROP TABLE IF EXISTS stg_category_translation;
CREATE TABLE stg_category_translation (
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100)
);
