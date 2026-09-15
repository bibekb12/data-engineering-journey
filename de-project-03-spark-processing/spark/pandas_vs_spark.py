import time

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col

FILE_PATH = "data/raw/yellow_tripdata_2025-01.parquet"

# Pandas

print("=== Pandas Benchmark ===")
start = time.perf_counter()
pdf = pd.read_parquet(FILE_PATH)

pandas_result = (
    pdf[(pdf["trip_distance"] > 0) & (pdf["fare_amount"] > 0)]
    .groupby("PULocationID")["fare_amount"]
    .mean()
    .sort_values(ascending=False)
)

pandas_time = time.perf_counter() - start

print(f"Pandas rows: {len(pdf):,}")
print(f"Pandas time: {pandas_time:.2f} seconds")

print("Top 10 Pandas results:")
print(pandas_result.head(10))

# Spart

print()
print("=== Spark Benchmark ===")

spark = SparkSession.builder.appName("Pandas-vs-Spark").master("local[*]").getOrCreate()

spark.sparkContext.setLogLevel("WARN")

start = time.perf_counter()

df = spark.read.parquet(FILE_PATH)

spark_result = (
    df.filter((col("trip_distance") > 0) & (col("fare_amount") > 0))
    .groupBy("PULocationID")
    .agg(avg("fare_amount").alias("avg_fare"))
    .orderBy(col("avg_fare").desc())
)

spark_result.show(10)

spark_time = time.perf_counter() - start

print(f"Spark time: {spark_time:.2f} seconds")


# --------------------------------------------------
# Comparison
# --------------------------------------------------

print()
print("=== Comparison ===")

print(f"Pandas: {pandas_time:.2f} seconds")
print(f"Spark:  {spark_time:.2f} seconds")

if spark_time < pandas_time:
    improvement = ((pandas_time - spark_time) / pandas_time) * 100
    print(f"Spark was {improvement:.1f}% faster.")
else:
    difference = ((spark_time - pandas_time) / pandas_time) * 100
    print(f"Pandas was {difference:.1f}% faster on this local test.")


spark.stop()
