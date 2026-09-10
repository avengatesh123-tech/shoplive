from pyspark import pipelines as dp


@dp.table(
    name="shoplive.bronze.products",
    comment="Raw product data ingested from CSV via Auto Loader",
)
def bronze_products():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("pathGlobFilter", "products.csv")
        .load("/Volumes/shoplive/core/raw/")
    )
