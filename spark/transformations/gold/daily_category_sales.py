from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="shoplive.gold.daily_category_sales",
    comment="Daily sales metrics by category",
)
def gold_daily_category_sales():
    orders_products_df = spark.read.table("orders_products")
    return (
        orders_products_df.groupBy("order_date", "category")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.sum("quantity").alias("total_quantity"),
            F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("total_revenue"),
            F.round(F.sum(F.col("quantity") * (F.col("unit_price") - F.col("unit_cost"))), 2).alias("total_profit"),
        )
        .select("order_date", "category", "total_orders", "total_quantity", "total_revenue", "total_profit")
        .orderBy("order_date", "category")
    )
