import pandas as pd
import pytest

from ingest import clean_weather_data


@pytest.fixture
def fake_api_reponse():
    """A small hardcoded fake response shaped like the real open_meteo output"""
    return {
        "hourly": {
            "time": ["2026-08-31T00:00", "2026-08-31T01:00", "2026-08-31T02:00"],
            "temperature_2m": [22.5, 21.8, None],
        }
    }


def test_clean_weather_data_returns_dataframe(fake_api_reponse):
    result = clean_weather_data(fake_api_reponse)
    assert isinstance(result, pd.DataFrame)


def test_clean_weather_data_has_expectd_columns(fake_api_reponse):
    result = clean_weather_data(fake_api_reponse)
    assert list(result.columns) == ["timestamp", "temperature_c"]


def test_clean_weather_data_handles_nulls(fake_api_reponse):
    result = clean_weather_data(fake_api_reponse)
    assert result["temperature_c"].isna().sum() == 0
    assert len(result) == 2


def test_clean_weather_data_timestamp_is_datetime(fake_api_reponse):
    result = clean_weather_data(fake_api_reponse)
    assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
