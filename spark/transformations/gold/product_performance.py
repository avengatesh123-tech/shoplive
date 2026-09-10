from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.product_performance",
    comment="Product-level sales performance metrics",
)
def gold_product_performance():
    orders_products_df = spark.read.table("orders_products")
    return (
        orders_products_df.groupBy("product_id", "product_name", "category")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.sum("quantity").alias("total_quantity_sold"),
            F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("total_revenue"),
            F.round(F.sum(F.col("quantity") * F.col("unit_cost")), 2).alias("total_cost"),
        )
        .withColumn("total_profit", F.round(F.col("total_revenue") - F.col("total_cost"), 2))
        .withColumn("profit_margin", F.round((F.col("total_profit") / F.col("total_revenue")) * 100, 2))
        .withColumn("average_selling_price", F.round(F.col("total_revenue") / F.col("total_quantity_sold"), 2))
        .select(
            "product_id", "product_name", "category",
            "total_orders", "total_quantity_sold", "total_revenue",
            "total_cost", "total_profit", "profit_margin", "average_selling_price",
        )
    )
