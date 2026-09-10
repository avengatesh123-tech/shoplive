from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.customers",
    comment="Customer enrichment with order aggregation metrics",
)
def gold_customers():
    customers_df = spark.read.table("shoplive.silver.customers")
    orders_df = spark.read.table("shoplive.silver.orders")
    return (
        customers_df.join(
            orders_df.groupBy("customer_id").agg(
                F.count("order_id").alias("total_orders"),
                F.sum("quantity").alias("total_items"),
                F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("total_spend"),
                F.round(F.avg(F.col("quantity") * F.col("unit_price")), 2).alias("average_order_value"),
                F.min("order_date").alias("first_order_date"),
                F.max("order_date").alias("last_order_date"),
            ),
            "customer_id", "left",
        )
        .select(
            "customer_id", "first_name", "second_name", "email",
            "city", "country", "signup_date", "signup_channel",
            F.coalesce("total_orders", F.lit(0)).alias("total_orders"),
            F.coalesce("total_items", F.lit(0)).alias("total_items"),
            F.coalesce("total_spend", F.lit(0.0)).alias("total_spend"),
            "average_order_value", "first_order_date", "last_order_date",
            F.coalesce(F.datediff(F.col("last_order_date"), F.col("first_order_date")), F.lit(0)).alias("customer_lifetime_days"),
        )
    )
