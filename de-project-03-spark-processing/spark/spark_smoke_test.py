from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("NYC-Taxi-Spark-Smoke-Test")
    .master("local[*]")
    .getOrCreate()
)

data = [
    ("Kathmandu", 24.5),
    ("Pokhara", 22.1),
    ("Biratnagar", 28.3),
]

df = spark.createDataFrame(data, ["city", "temperature"])

print("=== Data ===")
df.show()

print("=== Row Count ===")
print(df.count())

spark.stop()
