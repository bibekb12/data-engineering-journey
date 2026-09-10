import logging

import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import text

logger = logging.getLogger(__name__)


def load_raw_weather(
    df: pd.DataFrame,
    lat: float,
    lon: float,
) -> None:
    """Load weather data into the raw.weather PostgreSQL table.

    Parameters
    ----------
    df:
        Cleaned weather DataFrame.
    lat:
        Latitude of the weather location.
    lon:
        Longitude of the weather location.
    database_url:
        SQLAlchemy-compatible PostgreSQL connection URL.
    """

    if df.empty:
        raise ValueError("Weather DataFrame is empty")

    data = df.copy()

    data["latitude"] = lat
    data["longitude"] = lon

    data = data[
        [
            "timestamp",
            "temperature_c",
            "latitude",
            "longitude",
        ]
    ]

    hook = PostgresHook(postgres_conn_id="postgres_warehouse")

    engine = hook.get_sqlalchemy_engine()

    logger.info(
        "Loading %d weather rows into raw.weather",
        len(data),
    )

    # data.to_sql(
    #     name="weather",
    #     schema="raw",
    #     con=engine,
    #     if_exists="append",
    #     index=False,
    # )

    # logger.info(
    #     "Successfully loaded %d rows into raw.weather",
    #     len(data),
    # )
    insert_sql = text("""
        INSERT INTO raw.weather (
            timestamp,
            temperature_c,
            latitude,
            longitude
        )
        VALUES (
            :timestamp,
            :temperature_c,
            :latitude,
            :longitude
        )
        ON CONFLICT (timestamp, latitude, longitude)
        DO NOTHING
        """)

    records = data.to_dict(orient="records")
    try:
        with engine.begin() as connection:
            result = connection.execute(insert_sql, records)

        logger.info(
            "Weather loading completed successfully. %d rows inserted.",
            result.rowcount,
        )

    finally:
        engine.dispose()
