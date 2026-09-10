from pyspark import pipelines as dp


@dp.materialized_view(
    name="shoplive.silver.products",
    comment="Deduplicated product data",
)
def silver_products():
    return (
        spark.read.table("shoplive.bronze.products")
        .dropDuplicates(["product_id"])
    )
