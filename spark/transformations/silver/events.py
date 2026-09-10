from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_date, date_format


@dp.materialized_view(
    name="shoplive.silver.events",
    comment="Cleaned event data with separate date and time columns",
)
def silver_events():
    return (
        spark.read.table("shoplive.bronze.events")
        .dropDuplicates(["event_id"])
        .withColumn("event_date", to_date(col("event_ts")))
        .withColumn("event_time", date_format(col("event_ts"), "HH:mm:ss"))
        .drop("event_ts")
    )
