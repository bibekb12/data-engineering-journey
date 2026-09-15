from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("NYC-Taxi-Analysis").master("local[*]").getOrCreate()
)

spark.sparkContext.setLogLevel("Warn")

file_path = "data/raw/yellow_tripdata_2025-01.parquet"

df = spark.read.parquet(file_path)

print("=== Total trips ===")
print(df.count())

# removing invalid trips

clean_df = df.filter((col("trip_distance") > 0) & (col("fare_amount") > 0))

print("=== Valid Trips ===")
print(clean_df.count())

print("=== Top 10 Pickup Locations ===")
(clean_df.groupBy("PULocationID").count().orderBy(col("count").desc()).show())

spark.stop()
