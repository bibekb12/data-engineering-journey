"""
phase 1 project: weather API ingestion pipeline.
Fetch hourly weather from Open-Meteo, cleans it, and write to parquet
"""

import logging
import time
from pathlib import Path

import pandas as pd
import requests

# configure loggin: timestamp + log level + message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"
DATA_DIR = Path("data")


def fetch_weather_data(lat: float, lon: float, retries: int = 3) -> dict:
    """
    Call the Open-Meteo API and return the parsed JSON response.
    The request is retried when it fails. The delay increases exponenetially after each failed attemp.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
    }

    for attempt in range(1, retries + 1):
        try:
            logger.info("API requrest attempt %d/%d", attempt, retries)
            response = requests.get(
                API_URL,
                params=params,
                timeout=10,
            )
            # Raise an execption for the HTTP errors like 404,500 etc
            response.raise_for_status()
            logger.info("Weather data fetched successfully")
            return response.json()
        except requests.RequestException as exec:
            logger.error(
                "API request failed on attemp %d/%d: %s", attempt, retries, exec
            )

            # Dont sleep after the final failed attempt.
            if attempt == retries:
                raise

            delay = 2**attempt
            logger.info("Retrying in %d seconds.....", delay)
            time.sleep(delay)
    # this should never be reached becasuse the final attempt raise the execption
    raise RuntimeError("Weather API requrest failed.")


def clean_weather_data(raw_json: dict) -> pd.DataFrame:
    """Convert the raw meteo JSON into a flat, typed DataFrame.
    Null temperateures are dropped than interpolated. For ingestion pipeline,
    we avoid inventing weather measurements were not supplied by the API"""

    hourly = raw_json["hourly"]
    timestamps = hourly["time"]
    temperatures = hourly["temperature_2m"]

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "temperature_c": temperatures,
        }
    )

    # convetring strings date into pd datetimes
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # remove rows where the API didnot provide the temperature
    df = df.dropna(subset=["temperature_c"])

    # make the temperature column explicitly numeric
    df["temperature_c"] = pd.to_numeric(df["temperature_c"])

    return df


def save_to_parquet(
    df: pd.DataFrame,
    filename: str = "weather_raw.parquet",
) -> Path:
    """write the cleaned DataFrame to a Parquet file under DATA_DIR."""

    # create the directory if it doesnt already exists

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    path = DATA_DIR / filename

    df.to_parquet(path, index=False)

    logger.info(
        "Saved %d rows to %s",
        len(df),
        path,
    )

    return path


def run_pipeline(lat: float, lon: float) -> Path:
    """Orchestrates fetch -> clean -> save."""
    logger.info("Starting weather ingestion pipeline for lat=%s, lon=%s", lat, lon)
    raw = fetch_weather_data(lat, lon)
    df = clean_weather_data(raw)
    path = save_to_parquet(df)

    logger.info("Pipeline completed.")

    return path


if __name__ == "__main__":
    run_pipeline(lat=27.7, lon=85.3)
