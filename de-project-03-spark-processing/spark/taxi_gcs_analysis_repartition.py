from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col

BUCKET = "de-project-02-gcp-warehouse-bibek"

INPUT_PATH = f"gs://{BUCKET}/" "spark/raw/yellow_taxi/yellow_tripdata_2025-01.parquet"

OUTPUT_PATH = f"gs://{BUCKET}/" "spark/results/avg_fare_by_pickup"

GCS_CONNECTOR = "/home/bibek/.ivy2.5.2/jars/" "gcs-connector-3.0.2-shaded.jar"

GCS_BLOCK_SIZE = 64 * 1024 * 1024


# ============================================================
# Spark Session
# ============================================================

spark = (
    SparkSession.builder.appName("Taxi GCS Analysis")
    .config(
        "spark.hadoop.fs.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
    )
    .config(
        "spark.hadoop.fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )
    .config(
        "spark.hadoop.google.cloud.auth.type",
        "APPLICATION_DEFAULT",
    )
    .config(
        "spark.hadoop.fs.gs.block.size",
        str(GCS_BLOCK_SIZE),
    )
    .config(
        "spark.hadoop.fs.gs.inputstream.buffer.size",
        str(GCS_BLOCK_SIZE),
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


print("=== Reading Taxi Data from GCS ===")
print(f"Input path: {INPUT_PATH}")

df = spark.read.parquet(INPUT_PATH)

print(f"Original partitions: { df.rdd.getNumPartitions()}")

df = df.repartition(8)

print(f"Repartitioned: {df.rdd.getNumPartitions()}")

row_count = df.count()

print(f"Input rows: {row_count:,}")
print(f"Input partitions: {df.rdd.getNumPartitions()}")


# ============================================================
# Inspect sample
# ============================================================

print("=== Sample Data ===")

df.select(
    "VendorID",
    "tpep_pickup_datetime",
    "PULocationID",
    "trip_distance",
    "fare_amount",
).show(5, truncate=False)


# ============================================================
# Clean data
# ============================================================

print("=== Cleaning Data ===")

clean_df = df.filter(
    (col("PULocationID").isNotNull())
    & (col("trip_distance") > 0)
    & (col("fare_amount") > 0)
)

# ===========================================================
# Inspect physical plan
# ===========================================================

print("=== Print physical plan ===")
clean_df.groupBy("PULocationID").agg(avg("fare_amount").alias("avg_fare")).explain(
    "formatted"
)
# ============================================================
# Analyze
# ============================================================

print("=== Calculating Average Fare by Pickup Location ===")

result = (
    clean_df.groupBy("PULocationID")
    .agg(avg("fare_amount").alias("avg_fare"))
    .orderBy(col("avg_fare").desc())
)


# ============================================================
# Display results
# ============================================================

print("=== Top 10 Pickup Locations ===")

result.show(10, truncate=False)


# ============================================================
# Write results to GCS
# ============================================================

print("=== Writing Results to GCS ===")

(result.write.mode("overwrite").parquet(OUTPUT_PATH))

print(f"Output path: {OUTPUT_PATH}")


# ============================================================
# Complete
# ============================================================

print("=== Job Complete ===")

spark.stop()
