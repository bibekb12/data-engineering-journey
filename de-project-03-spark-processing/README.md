# DE Project 03 — Spark Processing

This project explores Apache Spark for processing NYC Yellow Taxi trip data, including local Spark processing, partitioning, GCS integration, and distributed execution with Google Cloud Dataproc.

# Project Overview

The project uses the January 2025 NYC Yellow Taxi dataset and demonstrates:

Reading Parquet data with Spark

Comparing Pandas and Spark

Inspecting Spark DataFrames

Understanding Spark partitions

Repartitioning DataFrames

Benchmarking different partition counts

Reading and writing data from Google Cloud Storage

Running PySpark jobs on Google Cloud Dataproc

Inspecting Spark physical execution plans

Performing aggregations by pickup location

## Project Structure
```
de-project-03-spark-processing/
├── README.md
├── .gitignore
└── spark/
    ├── inspect_taxi.py
    ├── pandas_vs_spark.py
    ├── partition_benchmark.py
    ├── partition_demo.py
    ├── repartition_demo.py
    ├── spark_smoke_test.py
    ├── taxi_analysis.py
    ├── taxi_gcs_analysis.py
    ├── taxi_gcs_analysis_repartition.py
    └── taxi_ui_demo.py

```
The raw taxi dataset and local virtual environment are intentionally excluded from Git.

## Dataset

The project uses:
```
yellow_tripdata_2025-01.parquet
```

The dataset contains approximately 3.48 million taxi trips for January 2025.

For the cloud-processing workflow, the dataset is stored in Google Cloud Storage:
```
gs://de-project-02-gcp-warehouse-bibek/spark/raw/yellow_taxi/yellow_tripdata_2025-01.parquet
```
## Local Spark Processing

The local scripts demonstrate Spark fundamentals such as:
- DataFrame creation

- Filtering
 
- Grouping
 
- Aggregation
 
- Sorting
 
- Partition inspection
 
- Repartitioning

For example:
```
df = spark.read.parquet(FILE_PATH)

result = (
    df.filter(
        (col("trip_distance") > 0)
        & (col("fare_amount") > 0)
    )
    .groupBy("PULocationID")
    .agg(avg("fare_amount").alias("avg_fare"))
    .orderBy(col("avg_fare").desc())
)
```
## Partitioning

The source Parquet data initially loaded with:
```
Original partitions: 2
```

The Dataproc experiment explicitly repartitioned the DataFrame:
```
df = df.repartition(8)
```

which resulted in:
```
Repartitioned: 8
```

The project also contains a partition benchmark comparing the original partitioning with 8 and 16 partitions.

## Dataproc Execution

A Google Cloud Dataproc cluster was created with:
```
Cluster: de-spark-cluster
Region: us-central1
Zone: us-central1-a
Master: e2-standard-2
Workers: 2 × e2-standard-2
Image: 2.2-debian12
```

The PySpark job was submitted with:
```
gcloud dataproc jobs submit pyspark \
  spark/taxi_gcs_analysis_repartition.py \
  --cluster=de-spark-cluster \
  --region=us-central1
```

The job completed successfully.

Spark Physical Plan

The repartitioned Dataproc job produced a physical plan containing:
```
Scan parquet
    ↓
Filter
    ↓
Project
    ↓
Exchange RoundRobinPartitioning(8)
    ↓
HashAggregate
    ↓
Exchange hashpartitioning(PULocationID, 1000)
    ↓
HashAggregate
```

This demonstrates an important Spark concept: operations such as repartition() and groupBy() can introduce shuffle stages represented by Exchange operators.

The Parquet scan also showed predicate pushdown:
```
PushedFilters:
[
  IsNotNull(trip_distance),
  IsNotNull(fare_amount),
  IsNotNull(PULocationID),
  GreaterThan(trip_distance,0.0),
  GreaterThan(fare_amount,0.0)
]
```
## Data Cleaning

Trips are filtered to remove invalid records:
```
clean_df = df.filter(
    (col("PULocationID").isNotNull())
    & (col("trip_distance") > 0)
    & (col("fare_amount") > 0)
)
```
## Analysis

The main analysis calculates the average fare by pickup location:
```
clean_df.groupBy("PULocationID") \
    .agg(avg("fare_amount").alias("avg_fare"))
```

The top results from the successful Dataproc run included:

|   Pickup Location	| Average Fare|
|:------------------: | :------------:|
|   27 |    78.81|   
|   5   |	72.17|   
|   1	|   72.10|   
|   265	|   68.98|   
|   204	|   64.64|   
|   93	|   64.42|   
|   132	|   62.65|   
|   199	|   56.20|   
|   219	|   54.45|   
|   207	|   52.60|   

These values represent averages of the fare_amount field after the basic data-quality filters.

## Output

The aggregated result is written back to Google Cloud Storage:
```
gs://de-project-02-gcp-warehouse-bibek/spark/results/avg_fare_by_pickup
```
### Key Spark Concepts Learned
## Lazy Evaluation

Transformations such as:
```
filter()
groupBy()
agg()
orderBy()
```

build a logical execution plan. Spark executes the plan when an action such as count(), show(), or write() is triggered.

## Repartitioning
```
df.repartition(8)
```

creates a new partitioning layout and introduces a shuffle.

## Aggregation Shuffle

A groupBy("PULocationID") requires records with the same pickup location to be brought together. The physical plan therefore contains a hash-partitioning exchange.

## Predicate Pushdown

Because the source is Parquet, Spark can push suitable filters toward the file scan, reducing unnecessary data processing.

## Distributed Processing

Running the same PySpark application through Dataproc demonstrates how Spark applications can move from local development to a distributed cluster.

## Cloud Workflow

The overall workflow is:
```
NYC Taxi Parquet
       ↓
Google Cloud Storage
       ↓
Dataproc Cluster
       ↓
PySpark
       ↓
Read Parquet
       ↓
Filter invalid trips
       ↓
Repartition
       ↓
Group by PULocationID
       ↓
Calculate average fare
       ↓
Write Parquet
       ↓
Google Cloud Storage
```
## Technologies

- Python

- PySpark

- Apache Spark

- Pandas
 
- Google Cloud Storage
 
- Google Cloud Dataproc
 
- Hadoop GCS Connector
 
- Git / GitHub
 
- Parquet

## Status

The Dataproc processing pipeline has been successfully executed, including GCS input, Spark repartitioning, physical-plan inspection, aggregation, and GCS output.