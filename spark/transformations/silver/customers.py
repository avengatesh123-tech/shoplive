from pyspark import pipelines as dp
from pyspark.sql.functions import split, col, regexp_replace


@dp.materialized_view(
    name="shoplive.silver.customers",
    comment="Cleaned customer data with split names and masked emails",
)
def silver_customers():
    return (
        spark.read.table("shoplive.bronze.customers")
        .withColumn("first_name", split(col("name"), " ")[0])
        .withColumn("second_name", split(col("name"), " ")[1])
        .drop("name")
        .withColumn("email", regexp_replace(col("email"), "(?<=.{2})[^@]+(?=@)", "***"))
        .dropDuplicates(["customer_id"])
    )

