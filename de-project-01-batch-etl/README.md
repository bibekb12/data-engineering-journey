# Batch ETL Pipeline with Airflow, PostgreSQL and dbt Overview

## This project is a small but production-oriented batch data pipeline built around weather data.

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
```
                         Weather API
                              |
                              v
                   +----------------------+
                   |   Python Extractor   |
                   |   API + cleaning     |
                   +----------+-----------+
                              |
                              v
                   weather_raw.parquet
                              |
                              v
                   +----------------------+
                   |     PostgreSQL       |
                   |     raw.weather      |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |     dbt staging      |
                   |     stg_weather       |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |      dbt mart        |
                   |   daily_weather      |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |     dbt tests        |
                   |      16 checks        |
                   +----------------------+

```
### Apache Airflow orchestrates the workflow

                                   Airflow Workflow
                                       extract
                                          |
                                          v
                                       load_raw
                                          |
                                          v
                                       dbt_run
                                          |
                                          v
                                       dbt_test

### Why I Built It This Way

One of the main goals of this project was to understand the difference between data processing and workflow orchestration.

Each tool has a specific responsibility:

Component	Responsibility
Python	Extract and prepare API data
PostgreSQL	Store raw and analytical data
dbt	Transform data and run data-quality tests
Airflow	Orchestrate the workflow
Docker Compose	Provide the local infrastructure
Git	Version control

This separation makes the pipeline easier to understand, maintain, test, and extend than putting the entire process into one large Python script.

Data Flow

The extraction task requests weather observations for a configured latitude and longitude.

The extracted data is cleaned and written to a Parquet file:

data/weather_raw.parquet


The load task reads that file and inserts the observations into:

raw.weather


The raw table intentionally contains the observations before analytical transformations are applied.

dbt then creates the staging model:

analytics.stg_weather


and the daily analytical table:

analytics.daily_weather


The final table contains daily weather summaries such as:

Minimum temperature
Maximum temperature
Average temperature
Observation count
Weather date
Latitude
Longitude
Airflow Orchestration

Apache Airflow is responsible for running the pipeline in the correct order.

The DAG contains four tasks:
```
            extract
               |
               v
            load_raw
               |
               v
            dbt_run
               |
               v
            dbt_test
```
### Task Responsibilities
extract

The extract task calls the weather API, cleans the returned data, and writes the result to a Parquet file.

Weather API
     |
     v
Python extractor
     |
     v
weather_raw.parquet

load_raw

The load_raw task reads the Parquet file and loads the observations into the PostgreSQL raw layer.

weather_raw.parquet
        |
        v
   raw.weather

dbt_run

The dbt_run task executes the dbt models.

It creates:

analytics.stg_weather
analytics.daily_weather

dbt_test

The final task runs the dbt data-quality tests.

If the tests fail, the pipeline is considered unsuccessful.

Failure Handling and Retries

The DAG is configured with retries for temporary failures:

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


This is particularly useful for API-based workloads because temporary network or service failures should not necessarily cause the entire scheduled pipeline to fail permanently.

The dependency chain also prevents downstream processing when an upstream task fails.

For example:

extract fails
     |
     X
load_raw does not run


Similarly:

load_raw fails
     |
     X
dbt_run does not run


And:

dbt_test fails
     |
     X
pipeline is considered unsuccessful

Configuration and Credentials

The weather coordinates are stored as Airflow Variables:

weather_latitude
weather_longitude


The PostgreSQL connection is stored as an Airflow Connection rather than putting database credentials directly into the DAG.

This keeps configuration separate from application logic and avoids hardcoding credentials into source code.

Sensitive configuration and local environment files are excluded from Git using .gitignore.

Idempotency

A repeated pipeline run should not create duplicate weather observations.

The raw table therefore has a uniqueness constraint:

UNIQUE ("timestamp", latitude, longitude)


This means that the same weather observation cannot be inserted multiple times for the same timestamp and coordinates.

I verified this against the running PostgreSQL database.

Current Result
Metric	Result
Total rows	168
Unique observations	168

The pipeline was executed repeatedly without increasing the number of unique observations.

This is an important property for batch pipelines because:

Airflow may retry tasks.
A pipeline may be manually rerun.
A scheduled run may need to be recovered after a failure.
Duplicate records should not accumulate in the raw layer.

The uniqueness constraint provides a database-level safeguard against duplicate observations.

Data Quality

dbt is used not only for transformations but also for data validation.

The project currently contains:

dbt component	Count
Models	2
Data tests	16
Sources	1

The latest test run completed successfully:

PASS = 16
WARN = 0
ERROR = 0
SKIP = 0


The tests currently validate that important fields such as:

Timestamp
Latitude
Longitude
Temperature
Minimum temperature
Maximum temperature
Average temperature
Observation count

are not null where required.

The tests are executed after the dbt transformations, so a successful pipeline means both the transformation and validation stages completed successfully.

Docker

The project uses Docker Compose to run the local infrastructure.

The main services include:

Apache Airflow API server
Apache Airflow scheduler
Apache Airflow worker
Apache Airflow DAG processor
Apache Airflow triggerer
PostgreSQL
Redis

The current environment uses:

Apache Airflow 3.3.1
PostgreSQL 16
Redis 7.2
dbt 1.12.4
dbt-postgres 1.11.0


Docker Compose makes the development environment reproducible without requiring Airflow and PostgreSQL to be installed directly on the host machine.

The project can therefore be developed and tested as a self-contained local data platform.

### Project Structure
```
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
├── config/
├── plugins/
├── docker-compose.yaml
├── .gitignore
└── README.md
```

Generated files such as:

Airflow logs
Python cache files
dbt target files
dbt logs
local Parquet data

are intentionally excluded from version control where appropriate.

Running the Project
1. Start the Services
docker compose up -d


Check the service status:

docker compose ps


All required services should be running and healthy.

2. Check the Airflow DAG

List the DAG:

docker compose exec airflow-worker \
  bash -c "airflow dags list | grep batch_etl"


List the tasks:

docker compose exec airflow-worker \
  bash -c "airflow tasks list batch_etl"


Expected tasks:

dbt_run
dbt_test
extract
load_raw

3. Trigger the Pipeline

Run the DAG manually:

docker compose exec airflow-worker \
  bash -c "airflow dags trigger batch_etl"


The DAG can also run automatically according to its configured schedule.

The DAG currently uses:

schedule="@daily"


with:

catchup=False

4. Access the Airflow UI

The Airflow web interface is available locally at:

http://localhost:8080


From the UI, you can inspect:

DAG runs
Task status
Task logs
Task dependencies
Execution history
Verifying the Results
Check the Raw Layer

Run:

docker compose exec postgres \
  psql -U warehouse_user -d warehouse \
  -c "SELECT COUNT(*) AS raw_rows FROM raw.weather;"


Current result:

raw_rows
--------
168

Check the Analytical Table

Run:

docker compose exec postgres \
  psql -U warehouse_user -d warehouse \
  -c "SELECT COUNT(*) AS daily_rows FROM analytics.daily_weather;"


Current result:

daily_rows
----------
7

Check for Duplicate Observations

Run:

docker compose exec postgres \
  psql -U warehouse_user -d warehouse \
  -c "
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT (timestamp, latitude, longitude)) AS unique_rows
FROM raw.weather;
"


Current result:

total_rows | unique_rows
-----------+------------
168        | 168


This confirms that all stored observations are unique according to the defined observation key.

Run dbt Tests

Run:

docker compose exec airflow-worker \
  bash -c "cd /opt/airflow/dbt/de_batch_etl && dbt test --profiles-dir ."


Expected result:

PASS=16
WARN=0
ERROR=0
SKIP=0
NO-OP=0
REUSED=0
TOTAL=16

Current Pipeline Results

The latest successful pipeline run produced:

Layer	Result
raw.weather	168 rows
analytics.daily_weather	7 rows
Unique raw observations	168
dbt models	2
dbt tests	16 passed
dbt warnings	0
dbt errors	0

The complete workflow successfully executed:
```
Weather API
     |
     v
   Extract
     |
     v
Parquet file
     |
     v
  PostgreSQL
  raw.weather
     |
     v
  dbt staging
     |
     v
  dbt mart
     |
     v
  dbt tests
     |
     v
  SUCCESS
```
## What I Learned

The most useful part of this project was seeing how the individual tools fit together.

Airflow is not the transformation engine. It coordinates the work.

dbt is not an orchestration platform. It handles SQL transformations and data quality.

PostgreSQL provides the storage and query layer.

Python handles the external API interaction and ingestion logic.

Docker provides the infrastructure needed to run the whole system consistently.

I also learned that reliability is more than making the "happy path" work.

A production-oriented pipeline needs to consider:

Retries
Logging
Idempotency
Data validation
Configuration management
Task dependencies
Reproducibility
Failure handling

These features become especially important when a pipeline needs to run repeatedly without manual intervention.

Design Decisions
Why PostgreSQL?

PostgreSQL provides a realistic relational database environment while remaining simple enough to run locally.

It also provides database-level constraints that can protect the raw layer from duplicate observations.

### Why dbt?

The analytical transformations are SQL-based, making dbt a natural fit.

dbt also provides:

Model dependency management
Data-quality testing
SQL-based transformations
A structured project layout
Reproducible analytical models
Why Airflow?

The pipeline contains multiple dependent stages:
```
extract
   |
   v
load
   |
   v
transform
   |
   v
test
```

This makes it a useful example of workflow orchestration rather than simply running a Python script manually.

Airflow provides task dependencies, retries, scheduling, logging, and execution monitoring.

## Why Docker Compose?

Running Airflow, PostgreSQL, and Redis through Docker makes the project easier to reproduce.

It also avoids requiring a complex host-level installation of the infrastructure.

### Why Keep a Raw Layer?

The raw layer provides a clear boundary between ingestion and transformation.

It makes it possible to inspect what was loaded before analytical transformations are applied.

The architecture therefore separates:
```
Raw data
   |
   v
Staging
   |
   v
Analytics
```

This makes debugging and future changes easier.

### Why Enforce Uniqueness?

Batch pipelines can be rerun and tasks can be retried.

A uniqueness constraint protects the raw layer from accumulating duplicate observations:

UNIQUE ("timestamp", latitude, longitude)


This makes the database itself responsible for enforcing an important data-integrity rule.

Future Improvements

Although the current pipeline works end-to-end, there are several areas that could be improved in a future version:

Add more comprehensive dbt tests such as accepted ranges and uniqueness tests.
Add incremental dbt models for larger datasets.
Add structured monitoring and alerting.
Add CI/CD checks using GitHub Actions.
Add automated unit tests for the extraction layer.
Add better API rate-limit handling.
Add partitioning for larger raw datasets.
Add a dedicated production secrets-management solution.
Add data lineage documentation.
Add dashboards for the analytical weather data.
Add deployment configuration for a cloud environment.

These improvements would allow the project to evolve from a local learning project into a more production-like data platform.

Conclusion

This project demonstrates a complete batch ETL workflow using a combination of Python, Apache Airflow, PostgreSQL, dbt, Docker, and Git.

The pipeline successfully:

Extracts weather data from an external API.
Cleans and stores the data as Parquet.
Loads the data into a PostgreSQL raw layer.
Prevents duplicate observations using a database constraint.
Transforms the data using dbt.
Produces daily analytical weather summaries.
Validates the transformed data with 16 dbt tests.
Orchestrates the entire workflow through Airflow.
Runs the infrastructure through Docker Compose.

The main goal was not to process a huge amount of data, but to understand how the individual components work together to create a reliable and maintainable batch data pipeline.