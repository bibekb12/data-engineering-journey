-- Active: 1788163553050@@localhost@5432@warehouse@public


create table dim_date (
    date_key integer primary key,
    full_date date not null,
    day integer not null,
    month integer not null,
    quarter integer not null,
    year integer not null
);

create table dim_customer (
    customer_key bigserial primary key,
    customer_unique_id varchar(50) not null,
    customer_id varchar(50) not null,

    customer_name varchar(255),
    customer_state varchar(5),
    customer_city varchar(255),
    customer_zip_code_prefix integer,

    effective_date date not null,
    end_date date,
    is_current BOOLEAN default TRUE
);


create table dim_product (
    product_key bigserial primary key,
    product_id varchar(50) not null,

    product_category varchar(255),
    product_name_length integer,
    product_description_length integer,
    product_photo_qty integer,
    product_weight_g numeric(10,2),
    product_length_cm numeric(10,2),
    product_height_cm numeric(10,2),
    product_width_cm numeric(10,2)
);


create table dim_seller (
    seller_key bigserial primary key,
    seller_id varchar(50) not null,
    seller_name varchar(255),
    seller_city varchar(255),
    seller_state varchar(5),
    seller_zip_prefix integer
);


CREATE TABLE fact_order_item (
    order_item_key  BIGSERIAL PRIMARY KEY,

    order_id        VARCHAR(50) NOT NULL,
    order_item_id   INTEGER NOT NULL,

    customer_key    BIGINT NOT NULL,
    product_key     BIGINT NOT NULL,
    seller_key      BIGINT NOT NULL,
    order_date_key  INTEGER NOT NULL,

    price           NUMERIC(12,2) NOT NULL,
    freight_value   NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_fact_seller
        FOREIGN KEY (seller_key)
        REFERENCES dim_seller(seller_key),

    CONSTRAINT fk_fact_order_date
        FOREIGN KEY (order_date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT uq_order_item
        UNIQUE (order_id, order_item_id)
);

