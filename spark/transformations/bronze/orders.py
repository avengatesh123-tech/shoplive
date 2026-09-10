from pyspark import pipelines as dp


@dp.table(
    name="shoplive.bronze.orders",
    comment="Raw order data ingested from CSV via Auto Loader",
)
def bronze_orders():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("pathGlobFilter", "orders_2026_h1.csv")
        .load("/Volumes/shoplive/core/raw/")
    )
