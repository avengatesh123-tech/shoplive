from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.customer_segments",
    comment="RFM-based customer segmentation",
)
def gold_customer_segments():
    orders_df = spark.read.table("shoplive.silver.orders")
    return (
        orders_df.groupBy("customer_id")
        .agg(
            F.datediff(F.current_date(), F.max("order_date")).alias("recency"),
            F.count("order_id").alias("frequency"),
            F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("monetary"),
        )
        .withColumn(
            "segment",
            F.when((F.col("recency") <= 30) & (F.col("frequency") >= 10) & (F.col("monetary") >= 50000), "VIP")
            .when((F.col("recency") <= 30) & (F.col("frequency") >= 5) & (F.col("monetary") >= 10000), "Loyal")
            .when((F.col("recency") > 30) & (F.col("recency") <= 90) & (F.col("frequency") >= 3), "At Risk")
            .when(F.col("recency") > 90, "Churned")
            .otherwise("New"),
        )
        .select("customer_id", "recency", "frequency", "monetary", "segment")
    )
