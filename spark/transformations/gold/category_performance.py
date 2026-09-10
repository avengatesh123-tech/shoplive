from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.category_performance",
    comment="Category-level sales performance metrics",
)
def gold_category_performance():
    orders_products_df = spark.read.table("orders_products")
    return (
        orders_products_df.groupBy("category")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.sum("quantity").alias("total_quantity"),
            F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("total_revenue"),
            F.round(F.sum(F.col("quantity") * F.col("unit_cost")), 2).alias("total_cost"),
        )
        .withColumn("total_profit", F.round(F.col("total_revenue") - F.col("total_cost"), 2))
        .withColumn("profit_margin", F.round((F.col("total_profit") / F.col("total_revenue")) * 100, 2))
        .withColumn("average_order_value", F.round(F.col("total_revenue") / F.col("total_orders"), 2))
        .select(
            "category", "total_orders", "total_quantity", "total_revenue",
            "total_cost", "total_profit", "profit_margin", "average_order_value",
        )
    )
