from datetime import datetime, timedelta
import logging
import pandas as pd

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

from ingestion.extract_weather import (
    extract_weather_to_parquet,
)
from ingestion.load_postgres import load_raw_weather

logger = logging.getLogger(__name__)

LATITUDE = 27.7
LONGITUDE = 85.3

RAW_FILE = "/opt/airflow/data/weather_raw.parquet"


def task_failure_callback(context):
    task_instance = context["task_instance"]

    logger.error(
        "Task failed: dag_id=%s, task_id=%s",
        task_instance.dag_id,
        task_instance.task_id,
    )


def extract():
    # print("Extracting API data ......")
    logger.info(
        "Starting weather extractor for lat=%s, lon=%s",
        LATITUDE,
        LONGITUDE,
    )
    return extract_weather_to_parquet(lat=LATITUDE, lon=LONGITUDE, output_path=RAW_FILE)


# def load_raw():
# print("Loading data into law layer .....")


def load_weather(**context):
    file_path = context["ti"].xcom_pull(task_ids="extract")
    logger.info(
        "Readinge extract file: %s",
        file_path,
    )
    df = pd.read_parquet(file_path)
    load_raw_weather(
        df=df,
        lat=LATITUDE,
        lon=LONGITUDE,
    )
    logger.info("Weather loading task started")


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": task_failure_callback,
}

with DAG(
    dag_id="batch_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    load_task = PythonOperator(
        task_id="load_raw",
        python_callable=load_weather,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt/de_batch_etl && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt/de_batch_etl && dbt test",
    )

    extract_task >> load_task >> dbt_run >> dbt_test
