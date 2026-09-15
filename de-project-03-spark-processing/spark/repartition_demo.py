from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("NYC-Taxi-Repartition-Demo")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


df = spark.read.parquet("data/raw/yellow_tripdata_2025-01.parquet")


print("=== Original Partitions ===")
print(df.rdd.getNumPartitions())


repartitioned_df = df.repartition(8)


print("=== After Repartition(8) ===")
print(repartitioned_df.rdd.getNumPartitions())


print("=== Triggering Repartition ===")

repartitioned_df.count()


print("=== Done ===")


spark.stop()
