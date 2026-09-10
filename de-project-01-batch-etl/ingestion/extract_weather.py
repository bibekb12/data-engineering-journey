import logging, requests, time
import pandas as pd
from pathlib import Path

"""Weather API extraction for the phase 4 batch ETL pipeline"""

logger = logging.getLogger(__name__)
API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather_data(lat: float, lon: float, retries: int = 3) -> dict:
    """Fetch hourly weather data
    Raises:
        requests.RequestExecption: If the API request fails"""

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
    }

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                "API request attempt %d/%d",
                attempt,
                retries,
            )

            response = requests.get(
                API_URL,
                params=params,
                timeout=10,
            )

            response.raise_for_status()

            logger.info("Weather API request successfully")
            return response.json()
        except requests.RequestException as exc:
            logger.error(
                "API request failed on attempt %d/%d: %s",
                attempt,
                retries,
                exc,
            )

            if attempt == retries:
                raise

            delay = 2**attempt

            logger.info("Retrying in %d seconds.......", delay)

            time.sleep(delay)
    raise RuntimeError("Weather API request failed.")


def clean_weather_data(raw_json: dict) -> pd.DataFrame:
    """Convert JSON into a typed DataFrame."""
    hourly = raw_json["hourly"]

    df = pd.DataFrame(
        {
            "timestamp": hourly["time"],
            "temperature_c": hourly["temperature_2m"],
        }
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["temperature_c"] = pd.to_numeric(
        df["temperature_c"],
        errors="coerce",
    )

    df = df.dropna(subset=["temperature_c"])

    logger.info(
        "Cleaned weather data: %d rows",
        len(df),
    )

    return df


def extract_weather_to_parquet(
    lat: float, lon: float, output_path: str = "data"
) -> str:
    logger.info(
        "Starting weather extraction for lat=%s, lon=%s",
        lat,
        lon,
    )
    raw_json = fetch_weather_data(lat, lon)
    df = clean_weather_data(raw_json)

    if df.empty:
        raise ValueError("Weather extraction returned no rows")

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        path,
        index=False,
    )
    return str(path)
