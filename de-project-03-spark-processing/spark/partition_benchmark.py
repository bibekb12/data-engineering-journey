import time
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("NYC-Taxi-Partition-Benchmark")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

file_path = "data/raw/yellow_tripdata_2025-01.parquet"

df = spark.read.parquet(file_path)


def benchmark(label, dataframe):
    start = time.perf_counter()
    row_count = dataframe.count()

    elapsed = time.perf_counter() - start

    print(f"{label}: " f"{row_count:,} rows " f"in {elapsed:.2f} seconds")


print("=== Partition Benchmark ===")

print(f"Original partitions: {df.rdd.getNumPartitions()}")

benchmark("Original", df)


df8 = df.repartition(8)

print(f"Repartitioned partitions: {df8.rdd.getNumPartitions()}")

benchmark("Repartition(8)", df8)


df16 = df.repartition(16)

print(f"Repartitioned partitions: {df16.rdd.getNumPartitions()}")

benchmark("Repartition(16)", df16)


spark.stop()
