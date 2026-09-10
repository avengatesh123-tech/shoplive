from pyspark import pipelines as dp


@dp.table(
    name="shoplive.bronze.events",
    comment="Raw event data ingested from JSON via Auto Loader",
)
def bronze_events():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("multiLine", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/Volumes/shoplive/core/event/")
    )
