-- Active: 1788163553050@@localhost@5432@warehouse@public
create database engineer;

create DATABASE warehouse;

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;



SELECT current_database();
SELECT current_schema();


-- warehouse row count

select 'dim_date' as table_name, count(*) as row_count from dim_date
union all 
select 'dim_customer', count(*) from dim_customer
union all 
select 'dim_product', count(*) from dim_product
union all 
select 'dim_seller', count(*) from dim_seller
union all 
select 'fact_order_item', count(*) from fact_order_item;


-- foreign key integrity check 

SELECT COUNT(*) AS missing_customer_keys
FROM fact_order_item
WHERE customer_key IS NULL;

SELECT COUNT(*) AS missing_product_keys
FROM fact_order_item
WHERE product_key IS NULL;

SELECT COUNT(*) AS missing_seller_keys
FROM fact_order_item
WHERE seller_key IS NULL;

SELECT COUNT(*) AS missing_date_keys
FROM fact_order_item f
LEFT JOIN dim_date d
    ON f.order_date_key = d.date_key
WHERE d.date_key IS NULL;



-- data duplication check


SELECT customer_id, COUNT(*)
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 1;



SELECT product_id, COUNT(*)
FROM dim_product
GROUP BY product_id
HAVING COUNT(*) > 1;


SELECT seller_id, COUNT(*)
FROM dim_seller
GROUP BY seller_id
HAVING COUNT(*) > 1;








-- CREATE TABLE dim_customer (
--     customer_key INT PRIMARY KEY,
--     customer_id VARCHAR(50),
--     customer_unique_id VARCHAR(50),
--     customer_name VARCHAR(255),
--     customer_state VARCHAR(50),
--     customer_city VARCHAR(100),
--     customer_zip_code_prefix INT,
--     effective_date DATE,
--     end_date DATE,
--     is_current BOOLEAN
-- );

-- CREATE TABLE dim_product (
--     product_key INT PRIMARY KEY,
--     product_id VARCHAR(50),
--     product_category VARCHAR(100),
--     product_name_length INT,
--     product_description_length INT,
--     product_photo_qty INT,
--     product_weight_g INT,
--     product_length_cm INT,
--     product_height_cm INT,
--     product_width_cm INT
-- );

-- CREATE TABLE dim_date (
--     date_key INT PRIMARY KEY,
--     full_date DATE,
--     day INT,
--     month INT,
--     quarter INT,
--     year INT
-- );

-- CREATE TABLE dim_seller (
--     seller_key INT PRIMARY KEY,
--     seller_id VARCHAR(50),
--     seller_name VARCHAR(255),
--     city VARCHAR(100),
--     state VARCHAR(50),
--     zip_prefix INT
-- );

-- CREATE TABLE fact_order_item (
--     order_item_key INT PRIMARY KEY,
--     order_id VARCHAR(50),
--     order_item_id INT,

--     customer_key INT,
--     product_key INT,
--     seller_key INT,
--     order_date_key INT,

--     price DECIMAL(12,2),
--     freight_value DECIMAL(12,2),

--     FOREIGN KEY (customer_key)
--         REFERENCES dim_customer(customer_key),

--     FOREIGN KEY (product_key)
--         REFERENCES dim_product(product_key),

--     FOREIGN KEY (seller_key)
--         REFERENCES dim_seller(seller_key),

--     FOREIGN KEY (order_date_key)
--         REFERENCES dim_date(date_key)
-- );
