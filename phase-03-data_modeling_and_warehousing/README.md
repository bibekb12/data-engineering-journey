# Phase 03 — Data Modeling & Warehousing

This phase transforms the Olist e-commerce datasets into a dimensional data warehouse using PostgreSQL.

The goal is to move from raw transactional CSV data to an analytical **star schema** that supports reporting and business analysis across customers, products, sellers, dates, and order items.

## Project Structure

```text
phase-03-data-modeling/
├── README.md
├── ![DESIGN.mf](DESIGN.md)
├── diagram/olist_erd.png
├── ddl/warehouse.sql
└── transform/
    └── load_warehouse.py
```
## ARCHITECURE
                    ┌───────────────┐
                    │   dim_date    │
                    │───────────────│
                    │ date_key (PK) │
                    │ full_date     │
                    │ day           │
                    │ month         │
                    │ quarter       │
                    │ year          │
                    └───────┬───────┘
                            │
                            │
┌─────────────────┐         │         ┌─────────────────┐
│  dim_customer   │         │         │   dim_product   │
│─────────────────│         │         │─────────────────│
│ customer_key PK │         │         │ product_key PK  │
│ customer_id     │         │         │ product_id      │
│ customer_name   │         │         │ product_category│
│ state           │         │         │ dimensions      │
│ city            │         │         │                 │
└────────┬────────┘         │         └────────┬────────┘
         │                  │                  │
         │                  │                  │
         │          ┌───────▼────────┐         │
         └─────────►│fact_order_item │◄────────┘
                    │────────────────│
                    │ order_id       │
                    │ order_item_id  │
                    │ customer_key   │
                    │ product_key    │
                    │ seller_key     │
                    │ order_date_key │
                    │ price          │
                    │ freight_value  │
                    └───────┬────────┘
                            │
                            │
                    ┌───────▼───────┐
                    │   dim_seller  │
                    │───────────────│
                    │ seller_key PK │
                    │ seller_id     │
                    │ seller_name   │
                    │ city          │
                    │ state         │
                    │ zip_prefix    │
                    └───────────────┘

## Data Loading Process

The Python ETL script performs the following steps:

Reads the source CSV files with pandas.
Creates the date dimension from order purchase timestamps.
Builds the customer dimension.
Builds the product dimension and translates product categories.
Builds the seller dimension.
Joins order items with orders.
Resolves natural keys to warehouse surrogate keys.
Generates the order date key.
Validates foreign-key lookups.
Loads the final fact table into PostgreSQL.
Performs warehouse row-count validation.

The main transformation script is:

transform/load_warehouse.py


## Database Configuration

The loader uses the following environment variables:

DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_NAME

Defaults are provided for local development:

DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=warehouse

Running the Loader

From the project root:

python phase-03-data-modeling/transform/load_warehouse.py

Or, if already inside the phase directory:

python transform/load_warehouse.py
Prerequisites

Install the required Python packages:

pip install pandas sqlalchemy psycopg2-binary

A running PostgreSQL database is also required.

The warehouse schema should be created using:

ddl.sql

before running the transformation script.

## Validation

The loader validates that every fact record can resolve its required dimension keys:

customer_key
product_key
seller_key

If any required foreign key is missing, the pipeline raises an error rather than loading invalid fact records.

The loader also reports the number of rows loaded into each warehouse table.

## Design Documentation

See ![DESIGN.md](DESIGN.md) for the detailed modeling decisions, including:

Fact table grain
Dimension design
Surrogate-key strategy
Date dimension design
Customer dimension design
Product dimension design
Seller dimension design
Star-schema rationale
ERD
Deliverables
File	Description
README.md	Phase overview and usage documentation
DESIGN.md	Data-modeling decisions
erd.png	Entity relationship diagram
ddl.sql	PostgreSQL warehouse schema
transform/load_warehouse.py	ETL/load pipeline
Outcome

The result is a PostgreSQL dimensional warehouse designed for analytical workloads.

The model provides a clear separation between:

Facts — measurable business transactions
Dimensions — descriptive business context

This structure makes it possible to answer questions such as:

What are total sales by month?
Which products generate the most revenue?
Which sellers have the highest sales?
How does freight cost vary by seller or product?
Which customer regions generate the most orders?
How does sales performance change over time?

## Future Improvements

Potential future enhancements include:

Add an order dimension for order-status analysis.
Add payment and review dimensions/facts.
Implement full Slowly Changing Dimension Type 2 processing for customers.
Add data-quality reporting.
Add incremental loading instead of append-only loading.
Add warehouse load metadata and audit tables.
Add indexes optimized for common analytical queries.