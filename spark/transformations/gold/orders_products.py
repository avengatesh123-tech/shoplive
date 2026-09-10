from pyspark import pipelines as dp
from pyspark.sql.functions import broadcast


@dp.temporary_view(name="orders_products")
def orders_products():
    orders_df = spark.read.table("shoplive.silver.orders")
    products_df = spark.read.table("shoplive.silver.products")
    return (
        orders_df.alias("o")
        .join(broadcast(products_df.alias("p")), "product_id")
        .select(
            "o.*",
            "p.product_name",
            "p.category",
            "p.unit_cost",
        )
    )
