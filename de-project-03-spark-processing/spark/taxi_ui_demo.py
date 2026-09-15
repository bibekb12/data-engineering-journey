from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("NYC-Taxi-Shuffle-Demo")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


file_path = "data/raw/yellow_tripdata_2025-01.parquet"

df = spark.read.parquet(file_path)


clean_df = df.filter((col("trip_distance") > 0) & (col("fare_amount") > 0))


result = clean_df.groupBy("PULocationID").count().orderBy(col("count").desc())


print("=== Top Pickup Locations ===")
result.show(20)


print()
print("Spark UI: http://localhost:4040")
print("Press Ctrl+C to stop Spark.")


input("Press Enter after inspecting the Spark UI...")


spark.stop()
