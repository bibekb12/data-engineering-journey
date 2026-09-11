import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

PROJECT_ID = "de-project-02-gcp-warehouse"
BUCKET = "gs://de-project-02-gcp-warehouse-bibek"
GCS_INPUT = f"{BUCKET}/raw/weather/weather.jsonl"

OBSERVATION_TIMESTAMP = "2026-09-11 00:00:00+00:00"


class ParseJson(beam.DoFn):

    def process(self, line):
        yield json.loads(line)


class CleanWeather(beam.DoFn):

    def process(self, record):
        temperature = record.get("temperature")

        if temperature is None:
            return

        yield {
            "city": record["city"],
            "country": record["country"],
            "latitude": float(record["latitude"]),
            "longitude": float(record["longitude"]),
            "temperature_c": float(temperature),
            "humidity_pct": float(record["humidity"]),
            "wind_speed_kmh": float(record["wind_speed"]),
            "pressure_hpa": float(record["pressure"]),
        }


class ToFactWeather(beam.DoFn):
    LOCATION_ID = {
        "Kathmandu": 1,
        "Pokhara": 2,
        "Biratnagar": 3,
    }

    def process(self, record):
        city = record["city"]
        location_id = self.LOCATION_ID.get(city)

        if location_id is None:
            return

        yield {
            "weather_id": f"20260911-{location_id}",
            "location_id": location_id,
            "observation_timestamp": OBSERVATION_TIMESTAMP,
            "observation_date": "2026-09-11",
            "temperature_c": record["temperature_c"],
            "humidity_pct": record["humidity_pct"],
            "wind_speed_kmh": record["wind_speed_kmh"],
            "pressure_hpa": record["pressure_hpa"],
        }


def main():

    options = PipelineOptions(
        runner="DataflowRunner",
        project=PROJECT_ID,
        region="asia-southeast1",
        worker_zone="asia-southeast1-b",
        temp_location=f"{BUCKET}/dataflow/temp",
        staging_location=f"{BUCKET}/dataflow/staging",
        service_account_email=(
            "de-etl-pipeline@de-project-02-gcp-warehouse.iam.gserviceaccount.com"
        ),
        job_name="weather-etl-v4",
        save_main_session=True,
        worker_machine_type="e2-standard-2",
    )

    table = f"{PROJECT_ID}:weather_warehouse.fact_weather"
    schema = {
        "fields": [
            {"name": "weather_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "location_id", "type": "INTEGER", "mode": "REQUIRED"},
            {
                "name": "observation_timestamp",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
            },
            {
                "name": "observation_date",
                "type": "DATE",
                "mode": "REQUIRED",
            },
            {"name": "temperature_c", "type": "FLOAT"},
            {"name": "humidity_pct", "type": "FLOAT"},
            {"name": "wind_speed_kmh", "type": "FLOAT"},
            {"name": "pressure_hpa", "type": "FLOAT"},
        ]
    }

    with beam.Pipeline(options=options) as pipeline:

        (
            pipeline
            | "Read raw weather from GCS" >> beam.io.ReadFromText(GCS_INPUT)
            | "Parse JSON" >> beam.ParDo(ParseJson())
            | "Clean weather" >> beam.ParDo(CleanWeather())
            | "Convert to fact schema" >> beam.ParDo(ToFactWeather())
            | "Write to BigQuery"
            >> beam.io.WriteToBigQuery(
                table=table,
                schema=schema,
                custom_gcs_temp_location=f"{BUCKET}/staging/bigquery-temp",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            )
        )


if __name__ == "__main__":
    main()
