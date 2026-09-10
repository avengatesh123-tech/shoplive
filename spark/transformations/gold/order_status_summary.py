from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.order_status_summary",
    comment="Order count and revenue by status",
)
def gold_order_status_summary():
    orders_df = spark.read.table("shoplive.silver.orders")
    return (
        orders_df.groupBy("status")
        .agg(
            F.count("order_id").alias("order_count"),
            F.sum("quantity").alias("total_quantity"),
            F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("total_revenue"),
        )
        .select("status", "order_count", "total_quantity", "total_revenue")
    )
