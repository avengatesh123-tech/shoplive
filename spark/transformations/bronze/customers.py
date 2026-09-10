from pyspark import pipelines as dp


@dp.table(
    name="shoplive.bronze.customers",
    comment="Raw customer data ingested from CSV via Auto Loader",
)
def bronze_customers():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("pathGlobFilter", "customers.csv")
        .load("/Volumes/shoplive/core/raw/")
    )
