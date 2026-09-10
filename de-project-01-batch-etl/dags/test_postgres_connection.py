from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def test_postgres_connection():
    hook = PostgresHook(postgres_conn_id="postgres_warehouse")

    print("Testing PostgreSQL connection...")

    result = hook.get_first("SELECT current_database(), current_user;")

    print(f"Database: {result[0]}")
    print(f"User: {result[1]}")

    print("PostgreSQL connection successful!")


with DAG(
    dag_id="test_postgres_connection",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    test_connection = PythonOperator(
        task_id="test_connection",
        python_callable=test_postgres_connection,
    )
