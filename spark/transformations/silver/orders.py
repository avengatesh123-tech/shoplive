from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_date, date_format


@dp.materialized_view(
    name="shoplive.silver.orders",
    comment="Cleaned order data with separate date and time columns",
)
def silver_orders():
    return (
        spark.read.table("shoplive.bronze.orders")
        .dropDuplicates(["order_id"])
        .withColumn("order_date", to_date(col("order_ts")))
        .withColumn("order_time", date_format(col("order_ts"), "HH:mm:ss"))
        .drop("order_ts")
    )
