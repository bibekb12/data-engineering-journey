
### `DESIGN.md`

```md
# Data Warehouse Design

![Olist Datawarehouse ERD](https://github.com/bibekb12/data-engineering-journey/blob/main/phase-03-data_modeling_and_warehousing/diagrams/olist_star_schema.png)

## 1. Overview

The warehouse uses a **star schema** designed around Olist order-item transactions.

The model contains one central fact table:

- `fact_order_item`

and four dimensions:

- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_seller`

The design separates transactional measures from descriptive attributes so that analytical queries remain simple and efficient.

---

## 2. Fact Table Grain

The grain of `fact_order_item` is:

> **One row per product item within an order.**

This grain matches the structure of the Olist order-items source dataset.

For example, if an order contains three different items, the fact table contains three rows for that order.

```text
order_id     order_item_id     product_id     seller_id
--------------------------------------------------------
ORDER_001    1                 PRODUCT_A     SELLER_X
ORDER_001    2                 PRODUCT_B     SELLER_Y
ORDER_001    3                 PRODUCT_C     SELLER_X