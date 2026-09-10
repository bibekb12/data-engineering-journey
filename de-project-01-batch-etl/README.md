Batch ETL Pipeline with Airflow, PostgreSQL and dbt
Overview

This project is a small but production-oriented batch data pipeline built around weather data.

The pipeline pulls weather observations from an external API, saves the raw data, loads it into PostgreSQL, transforms it with dbt, and runs data-quality checks before considering the pipeline successful.

I built this project to get hands-on experience with the pieces that commonly appear together in modern data engineering workflows:

Python for data extraction
Apache Airflow for orchestration
PostgreSQL as the warehouse
dbt for SQL transformations and testing
Docker Compose for local infrastructure
Git for version control

The project is intentionally small in terms of data volume. The focus is on building the pipeline correctly: separating responsibilities, handling failures, preventing duplicate records, and making the workflow reproducible.

Architecture
                  Weather API
                       |
                       v
              +------------------+
              | Python Extractor  |
              | API + cleaning    |
              +---------+---------+
                        |
                        v
              weather_raw.parquet
                        |
                        v
              +------------------+
              |   PostgreSQL     |
              |   raw.weather    |
              +---------+---------+
                        |
                        v
              +------------------+
              |   dbt staging    |
              |   stg_weather    |
              +---------+---------+
                        |
                        v
              +------------------+
              |    dbt mart      |
              | daily_weather    |
              +---------+---------+
                        |
                        v
              +------------------+
              |   dbt tests      |
              |   16 checks      |
              +------------------+

        Apache Airflow orchestrates the workflow


The Airflow workflow is:

extract
   ↓
load_raw
   ↓
dbt_run
   ↓
dbt_test

Why I built it this way

One of the main goals of this project was to understand the difference between data processing and workflow orchestration.

Python is responsible for extracting and preparing the API data.

PostgreSQL stores the data.

dbt is responsible for SQL transformations and data-quality tests.

Airflow coordinates everything and determines the order in which the tasks run.

This separation makes the pipeline easier to understand and maintain than putting the entire process into one large Python script.

Data flow

The extraction task requests weather observations for a configured latitude and longitude.

The extracted data is cleaned and written to a Parquet file:

data/weather_raw.parquet


The load task reads that file and inserts the observations into:

raw.weather


The raw table intentionally contains the observations before the analytical transformations are applied.

dbt then creates the staging model:

analytics.stg_weather


and the daily analytical table:

analytics.daily_weather


The final table contains daily weather summaries such as minimum temperature, maximum temperature, average temperature, and observation count.

Airflow orchestration

Airflow is responsible for running the pipeline in the correct order.

The DAG contains four tasks:

extract
   ↓
load_raw
   ↓
dbt_run
   ↓
dbt_test


If extraction fails, the downstream tasks do not run.

If loading fails, dbt does not run.

If the dbt tests fail, the pipeline is considered unsuccessful.

This gives the workflow a clear dependency chain instead of treating each script as an independent process.

The DAG also uses retries for temporary failures.

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


This is particularly useful for API-based workloads because temporary network or service failures should not necessarily cause the entire scheduled pipeline to fail permanently.

Configuration and credentials

The weather coordinates are stored as Airflow Variables:

weather_latitude
weather_longitude


The PostgreSQL connection is stored as an Airflow Connection rather than putting database credentials directly into the DAG.

This keeps configuration separate from application logic and avoids hardcoding credentials into source code.

Secrets and local environment configuration are excluded from Git using .gitignore.

Idempotency

A repeated pipeline run should not create duplicate weather observations.

The raw table therefore has a uniqueness constraint:

UNIQUE ("timestamp", latitude, longitude)


This means that the same weather observation cannot be inserted multiple times for the same timestamp and coordinates.

I also verified this against the running database.

Current result:

total_rows     = 168
unique_rows    = 168


The pipeline was executed repeatedly without increasing the number of unique observations.

This is an important property for batch pipelines because Airflow may retry tasks or a pipeline may be manually rerun after a failure.

Data quality

dbt is used not only for transformations but also for data validation.

The project currently contains:

2 models
16 data tests
1 source


The final test run completed successfully:

PASS = 16
WARN = 0
ERROR = 0
SKIP = 0


The tests currently validate that important fields such as timestamps, coordinates, temperatures, and observation counts are not null.

The tests are executed after the dbt transformations, so a successful pipeline means both the transformation and validation stages completed successfully.

Docker

The project uses Docker Compose to run the local infrastructure.

The main services include:

Apache Airflow
PostgreSQL
Redis
Airflow scheduler
Airflow worker
Airflow API server
Airflow DAG processor
Airflow triggerer

This makes the development environment reproducible without requiring Airflow and PostgreSQL to be installed directly on the host machine.

The project can therefore be developed and tested as a self-contained local data platform.

Project structure
de-project-01-batch-etl/
│
├── dags/
│   ├── batch_etl.py
│   └── test_postgres_connection.py
│
├── ingestion/
│   ├── extract_weather.py
│   ├── load_postgres.py
│   ├── test_load.py
│   └── __init__.py
│
├── dbt/
│   └── de_batch_etl/
│       ├── models/
│       ├── tests/
│       ├── dbt_project.yml
│       └── profiles.yml
│
├── sql/
│   ├── init/
│   │   └── 01-create_warehouse.sql
│   └── raw_weather.sql
│
├── docs/
├── data/
├── docker-compose.yaml
├── .gitignore
└── README.md


Generated files such as Airflow logs, Python cache files, and dbt build artifacts are intentionally excluded from version control.

Running the project

Start the services:

docker compose up -d


Check service health:

docker compose ps


Trigger the Airflow DAG:

docker compose exec airflow-worker \
  bash -c "airflow dags trigger batch_etl"


The Airflow UI is available at:

http://localhost:8080


The DAG can also be scheduled automatically using its configured schedule.

Verifying the results

Check the raw layer:

docker compose exec postgres \
  psql -U warehouse_user -d warehouse \
  -c "SELECT COUNT(*) AS raw_rows FROM raw.weather;"


Check the analytical table:

docker compose exec postgres \
  psql -U warehouse_user -d warehouse \
  -c "SELECT COUNT(*) AS daily_rows FROM analytics.daily_weather;"


Run dbt tests:

docker compose exec airflow-worker \
  bash -c "cd /opt/airflow/dbt/de_batch_etl && dbt test --profiles-dir ."


A successful run currently produces:

raw.weather              168 rows
analytics.daily_weather    7 rows
dbt tests                 16 passed

What I learned

The most useful part of this project was seeing how the individual tools fit together.

Airflow is not the transformation engine. It coordinates the work.

dbt is not an orchestration platform. It handles SQL transformations and data quality.

PostgreSQL provides the storage and query layer.

Python handles the external API interaction and ingestion logic.

Docker provides the infrastructure needed to run the whole system consistently.

I also learned that reliability is more than making the "happy path" work. Retries, logging, idempotency, data validation, configuration management, and clear task dependencies all matter when a pipeline needs to run repeatedly without manual intervention.

Design decisions
Why PostgreSQL?

PostgreSQL provides a realistic relational warehouse environment while remaining simple enough to run locally.

Why dbt?

The analytical transformations are SQL-based, making dbt a natural fit. It also provides a structured way to define tests and dependencies between models.

Why Airflow?

The pipeline contains multiple dependent stages, making it a useful example of workflow orchestration rather than simply running a Python script manually.

Why Docker Compose?

Running Airflow and PostgreSQL locally through Docker makes the project easier to reproduce and avoids requiring a complex host-level installation.

Why keep a raw layer?

The raw layer provides a clear boundary between ingestion and transformation. It also makes it possible to inspect what was loaded before analytical transformations are applied.

Why enforce uniqueness?

Batch pipelines can be rerun and tasks can be retried. A uniqueness constraint protects the raw layer from accumulating duplicate observations.
