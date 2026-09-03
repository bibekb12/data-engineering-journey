import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Database configuration

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "warehouse")


DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}" f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# CSV location
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"


CUSTOMER_FILE = DATA_DIR / "olist_customers_dataset.csv"
ORDER_ITEM_FILE = DATA_DIR / "olist_order_items_dataset.csv"
ORDER_FILE = DATA_DIR / "olist_orders_dataset.csv"
PRODUCTS_FILE = DATA_DIR / "olist_products_dataset.csv"
SELLER_FILE = DATA_DIR / "olist_sellers_dataset.csv"
TRANSLATION_FILE = DATA_DIR / "product_category_name_translation.csv"

# Helpers


def make_date_key(series):
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y%m%d").astype("Int64")


def load_csv(path):
    print(f"Reading {path.name} ..........")

    df = pd.read_csv(path)

    print(f" Rows: {len(df):,}")
    print(f" Columns: {len(df.columns)}")

    return df


def clean_string_cloumns(df):
    """
    Convert NaN to None-compatible values
    """
    return df.where(pd.notnull(df), None)


# dimension date


def load_dim_date(orders):
    print("\n Loading dim_date......")

    dates = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce").dt.date

    dates = pd.Series(dates.dropna().unique())

    date_df = pd.DataFrame({"full_date": dates})

    date_df["full_date"] = pd.to_datetime(date_df["full_date"])

    # breakpoint()

    # date_df["date_key"] = (
    #     date_df["full_date"].dt.year * 1000
    #     + date_df["full_date"].dt.month * 100
    #     + date_df["full_date"].dt.day
    # )

    date_df["date_key"] = make_date_key(date_df["full_date"])

    date_df["day"] = date_df["full_date"].dt.day
    date_df["month"] = date_df["full_date"].dt.month
    date_df["quarter"] = date_df["full_date"].dt.quarter
    date_df["year"] = date_df["full_date"].dt.year

    date_df = date_df[
        [
            "date_key",
            "full_date",
            "day",
            "month",
            "quarter",
            "year",
        ]
    ]

    date_df.to_sql(
        "dim_date",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f" Loaded {len(date_df):,} dates")


def load_dim_customer(customers, orders):
    print("\n Loading dim customer......")

    # find the earliest purchase date for each customer

    order_dates = (
        orders[
            [
                "customer_id",
                "order_purchase_timestamp",
            ]
        ]
    ).copy()

    order_dates["order_purchase_timestamp"] = pd.to_datetime(
        order_dates["order_purchase_timestamp"],
        errors="coerce",
    )

    first_order = (
        order_dates.groupby("customer_id")["order_purchase_timestamp"]
        .min()
        .reset_index()
    )

    first_order["effective_date"] = first_order["order_purchase_timestamp"].dt.date

    customer_df = customers.merge(
        first_order[
            [
                "customer_id",
                "effective_date",
            ]
        ],
        on="customer_id",
        how="left",
    )

    # Fallback in the case a customer has no macthing order

    customer_df["effective_date"] = customer_df["effective_date"].fillna(
        pd.Timestamp("2016-01-01").date()
    )

    customer_df["end_date"] = None
    customer_df["is_current"] = True

    customer_df = customer_df.rename(
        columns={
            "customer_unique_id": "customer_unique_id",
            "customer_id": "customer_id",
            "customer_zip_code_prefix": "customer_zip_code_prefix",
            "customer_city": "customer_city",
            "customer_state": "customer_state",
        }
    )
    customer_df = customer_df[
        [
            "customer_unique_id",
            "customer_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix",
            "effective_date",
            "end_date",
            "is_current",
        ]
    ]

    # if csv customer doesnot contain customer_name
    customer_df["customer_name"] = None

    customer_df = customer_df[
        [
            "customer_unique_id",
            "customer_id",
            "customer_name",
            "customer_state",
            "customer_city",
            "customer_zip_code_prefix",
            "effective_date",
            "end_date",
            "is_current",
        ]
    ]

    customer_df.to_sql(
        "dim_customer",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f" Loaded {len(customer_df):,} customers")


# dimension product


def load_dim_product(products, translation):
    print("\n Loading dim product..........")

    # Translate portuguese category names to english
    product_df = products.merge(
        translation,
        on="product_category_name",
        how="left",
    )

    product_df["product_category"] = product_df["product_category_name_english"].fillna(
        product_df["product_category_name"]
    )

    product_df = product_df.rename(
        columns={
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length",
            "product_photos_qty": "product_photo_qty",
            "product_weight_g": "product_weight_g",
            "product_length_cm": "product_length_cm",
            "product_height_cm": "product_height_cm",
            "product_width_cm": "product_width_cm",
        }
    )
    product_df = product_df[
        [
            "product_id",
            "product_category",
            "product_name_length",
            "product_description_length",
            "product_photo_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ]

    product_df.to_sql(
        "dim_product",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f"  Loaded {len(product_df):,} products")


# dimension seller


def load_dim_seller(sellers):
    print("\n Loading dim seller...........")

    seller_df = sellers.rename(
        columns={
            "seller_zip_code_prefix": "seller_zip_prefix",
            "seller_city": "seller_city",
            "seller_state": "seller_state",
        }
    )

    seller_df["seller_name"] = None

    seller_df = seller_df[
        [
            "seller_id",
            "seller_name",
            "seller_city",
            "seller_state",
            "seller_zip_prefix",
        ]
    ]

    seller_df.to_sql(
        "dim_seller",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f" loaded {len(seller_df):,} sellers")


# fact order item


def load_fact_order_item(orders, order_items):
    print("\n Loading fact order item.........")

    # customer_id and order_purchase_timestamp from orders

    order_lookup = orders[
        [
            "order_id",
            "customer_id",
            "order_purchase_timestamp",
        ]
    ].copy()

    order_lookup["order_purchase_timestamp"] = pd.to_datetime(
        order_lookup["order_purchase_timestamp"],
        errors="coerce",
    )

    fact_df = order_items.merge(
        order_lookup,
        on="order_id",
        how="inner",
    )

    print(f" Joined order items: {len(fact_df):,}")

    # customer surrogate key

    customer_keys = pd.read_sql(
        text("""
            select customer_key, customer_id from dim_customer
            """),
        engine,
    )
    fact_df = fact_df.merge(
        customer_keys,
        on="customer_id",
        how="left",
    )

    # product surrogate key

    product_keys = pd.read_sql(
        text("""select product_key, product_id from dim_product"""),
        engine,
    )

    fact_df = fact_df.merge(
        product_keys,
        on="product_id",
        how="left",
    )

    # seller surrogate key

    seller_keys = pd.read_sql(
        text("""select seller_key, seller_id from dim_seller"""),
        engine,
    )

    fact_df = fact_df.merge(
        seller_keys,
        on="seller_id",
        how="left",
    )

    # date key

    # fact_df["order_date_key"] = (
    #     fact_df["order_purchase_timestamp"].dt.year * 1000
    #     + fact_df["order_purchase_timestamp"].dt.month * 100
    #     + fact_df["order_purchase_timestamp"].dt.day
    # )

    fact_df["order_date_key"] = make_date_key(fact_df["order_purchase_timestamp"])

    # validate foreign keys

    missing_customer = fact_df["customer_key"].isna().sum()
    missing_product = fact_df["product_key"].isna().sum()
    missing_seller = fact_df["seller_key"].isna().sum()

    print(f" Missing customer keys: {missing_customer:,}")
    print(f" Missing product keys: {missing_product:,}")
    print(f" Missing seller keys: {missing_seller:,}")

    if missing_customer > 0:
        raise ValueError("Some order item have no customer dimension key.")
    if missing_product > 0:
        raise ValueError("Some order item have no product dimension key.")
    if missing_seller > 0:
        raise ValueError("Some order item have no seller dimension key.")

    # build final fact table

    fact_df = fact_df[
        [
            "order_id",
            "order_item_id",
            "customer_key",
            "product_key",
            "seller_key",
            "order_date_key",
            "price",
            "freight_value",
        ]
    ]

    fact_df.to_sql(
        "fact_order_item",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f" Loaded {len(fact_df):,} order items")


# validation


def validation_warehouse():
    print("\n validating warehouse.......")

    tables = [
        "dim_date",
        "dim_customer",
        "dim_product",
        "dim_seller",
        "fact_order_item",
    ]

    with engine.connect() as conn:
        for table in tables:
            result = conn.execute(text(f"select count(*) from {table}"))
            count = result.scalar()
            print(f" {table:<20}{count:>10,} rows")


def truncate_warehouse():
    print("=" * 60)
    print("\nClearing warehouse...")
    print("=" * 60)
    with engine.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                fact_order_item,
                dim_customer,
                dim_product,
                dim_seller,
                dim_date
            RESTART IDENTITY CASCADE;
        """))
    print("=" * 60)
    print("Warehouse cleared.")
    print("=" * 60)


def main():

    # cleaning table before load
    truncate_warehouse()

    print("=" * 60)
    print("Starting olist data warehouse load")
    print("=" * 60)

    # read source data

    customers = load_csv(CUSTOMER_FILE)
    orders = load_csv(ORDER_FILE)
    order_items = load_csv(ORDER_ITEM_FILE)
    products = load_csv(PRODUCTS_FILE)
    sellers = load_csv(SELLER_FILE)
    translation = load_csv(TRANSLATION_FILE)

    # load dimensions

    load_dim_date(
        orders,
    )

    load_dim_customer(
        customers,
        orders,
    )

    load_dim_product(
        products,
        translation,
    )

    load_dim_seller(
        sellers,
    )

    # load fact

    load_fact_order_item(
        orders,
        order_items,
    )

    # validate

    validation_warehouse()

    print("\n" + "=" * 60)
    print("warehouse loading complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
