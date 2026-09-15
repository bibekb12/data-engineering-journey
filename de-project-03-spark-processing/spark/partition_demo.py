from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("NYC-Taxi-Partition-Demo")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("Warn")

df = spark.read.parquet("data/raw/yellow_tripdata_2025-01.parquet")

print("=== Spark Partition ===")
print(df.rdd.getNumPartitions())

print("=== Total Rows ===")
print(df.count())

print("=== Rows Per Partition === ")
partition_counts = df.rdd.mapPartitions(lambda rows: [sum(1 for _ in rows)]).collect()

for partition_id, count in enumerate(partition_counts):
    print(f"Partition {partition_id} : {count:,} rows")

spark.stop()
