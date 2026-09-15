from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("NYC-Taxi-Inspection").master("local[*]").getOrCreate()
)

spark.sparkContext.setLogLevel("Warn")

file_path = "data/raw/yellow_tripdata_2025-01.parquet"

df = spark.read.parquet(file_path)

print("=== schema ===")
df.printSchema()

print("=== Row docs ===")
print(df.count())

print("=== Sample docks ====")
df.show(5, truncate=False)

spark.stop()
