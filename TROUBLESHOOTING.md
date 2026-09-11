# Troubleshooting Guide

This guide provides solutions to common issues encountered when working with the ShopLive platform.

## Table of Contents

* [Pipeline Issues](#pipeline-issues)
* [Data Quality Issues](#data-quality-issues)
* [Performance Issues](#performance-issues)
* [Auto Loader Issues](#auto-loader-issues)
* [Unity Catalog Issues](#unity-catalog-issues)
* [Streaming Issues](#streaming-issues)
* [General Debugging](#general-debugging)

---

## Pipeline Issues

### Issue: Pipeline Fails to Start

**Symptoms:**
* Pipeline shows "FAILED" status immediately
* Error: "Unable to start pipeline"

**Solutions:**

1. **Check Permissions**
   \`\`\`sql
   -- Verify catalog permissions
   SHOW GRANTS ON CATALOG shoplive;
   SHOW GRANTS ON SCHEMA shoplive.bronze;
   \`\`\`

2. **Verify Storage Location**
   \`\`\`python
   # Check if storage path exists
   dbutils.fs.ls("/pipelines/shoplive/bronze")
   \`\`\`

3. **Check Cluster Configuration**
   * Ensure cluster has sufficient resources
   * Verify DBR version compatibility (14.3 LTS+)

4. **Review Pipeline Configuration**
   * Verify notebook path is correct
   * Check target schema exists
   * Ensure library dependencies are available

---

### Issue: Pipeline Stuck in "RUNNING" State

**Symptoms:**
* Pipeline runs for hours without completing
* No progress in update logs

**Solutions:**

1. **Check for Blocking Operations**
   \`\`\`sql
   -- Find long-running queries
   SELECT 
     query_id,
     query_text,
     execution_status,
     start_time,
     TIMESTAMPDIFF(MINUTE, start_time, CURRENT_TIMESTAMP()) as runtime_minutes
   FROM system.query.history
   WHERE start_time >= CURRENT_DATE
     AND execution_status = 'RUNNING'
   ORDER BY runtime_minutes DESC;
   \`\`\`

2. **Review Checkpoint State**
   * Check if checkpoint directory is corrupted
   * Consider resetting checkpoints (will reprocess data)

3. **Kill and Restart**
   * Stop the pipeline manually
   * Clear checkpoint (if needed)
   * Restart pipeline

---

### Issue: "Table Not Found" Error

**Symptoms:**
* Error: "Table 'shoplive.bronze.customers' not found"
* Pipeline fails during silver/gold layer processing

**Solutions:**

1. **Verify Table Exists**
   \`\`\`sql
   SHOW TABLES IN shoplive.bronze;
   \`\`\`

2. **Check Table Permissions**
   \`\`\`sql
   SHOW GRANTS ON TABLE shoplive.bronze.customers;
   \`\`\`

3. **Run Bronze Pipeline First**
   * Ensure bronze tables are created before running silver
   * Check task dependencies in job configuration

4. **Verify Catalog Context**
   \`\`\`python
   # In notebook
   spark.sql("USE CATALOG shoplive")
   spark.sql("USE SCHEMA bronze")
   \`\`\`

---

## Data Quality Issues

### Issue: High Null Counts

**Symptoms:**
* Many null values in critical columns
* Data quality checks failing

**Solutions:**

1. **Investigate Source Data**
   \`\`\`sql
   -- Check null distribution
   SELECT 
     COUNT(*) as total,
     COUNT(customer_id) as non_null_ids,
     COUNT(*) - COUNT(customer_id) as null_ids,
     ROUND(100.0 * (COUNT(*) - COUNT(customer_id)) / COUNT(*), 2) as null_pct
   FROM shoplive.bronze.customers;
   \`\`\`

2. **Add Null Filtering**
   \`\`\`python
   # In silver transformation
   df = df.filter(F.col("customer_id").isNotNull())
   \`\`\`

3. **Implement Default Values**
   \`\`\`python
   df = df.fillna({
       'country': 'UNKNOWN',
       'phone': '',
       'address': ''
   })
   \`\`\`

4. **Update Data Validation Rules**
   * Add expectations in pipelines
   * Set up data quality alerts

---

### Issue: Duplicate Records

**Symptoms:**
* Multiple records with same ID
* Counts don't match between layers

**Solutions:**

1. **Identify Duplicates**
   \`\`\`sql
   -- Find duplicate customer IDs
   SELECT 
     customer_id,
     COUNT(*) as record_count
   FROM shoplive.bronze.customers
   GROUP BY customer_id
   HAVING COUNT(*) > 1
   ORDER BY record_count DESC;
   \`\`\`

2. **Add Deduplication Logic**
   \`\`\`python
   # Keep most recent record
   from pyspark.sql.window import Window
   
   window = Window.partitionBy("customer_id").orderBy(F.col("_metadata.file_modification_time").desc())
   
   df = df.withColumn("row_num", F.row_number().over(window)) \
          .filter(F.col("row_num") == 1) \
          .drop("row_num")
   \`\`\`

3. **Check Source System**
   * Verify source data quality
   * Investigate why duplicates are being created

---

### Issue: Schema Evolution Failures

**Symptoms:**
* Error: "Schema mismatch"
* New columns not appearing in tables

**Solutions:**

1. **Enable Schema Evolution**
   \`\`\`python
   df.write \
     .format("delta") \
     .mode("append") \
     .option("mergeSchema", "true") \
     .save("/path/to/table")
   \`\`\`

2. **Check Auto Loader Configuration**
   \`\`\`python
   df = spark.readStream \
     .format("cloudFiles") \
     .option("cloudFiles.schemaEvolutionMode", "addNewColumns") \
     .load("/Volumes/shoplive/core/raw/")
   \`\`\`

3. **Manually Add Columns**
   \`\`\`sql
   ALTER TABLE shoplive.bronze.customers 
   ADD COLUMNS (
     new_column STRING COMMENT 'New field added'
   );
   \`\`\`

---

## Performance Issues

### Issue: Slow Query Performance

**Symptoms:**
* Queries take longer than expected
* Dashboard refreshes are slow

**Solutions:**

1. **Optimize with Z-ORDER**
   \`\`\`sql
   OPTIMIZE shoplive.gold.customer_segments
   ZORDER BY (segment, customer_id);
   \`\`\`

2. **Add Partitioning**
   \`\`\`sql
   CREATE TABLE shoplive.silver.orders (
     order_id STRING,
     customer_id STRING,
     order_date DATE,
     ...
   )
   PARTITIONED BY (order_date);
   \`\`\`

3. **Use Caching**
   \`\`\`python
   # Cache frequently accessed data
   df = spark.table("shoplive.silver.customers").cache()
   \`\`\`

4. **Analyze Query Plans**
   \`\`\`sql
   EXPLAIN EXTENDED
   SELECT * FROM shoplive.gold.customer_segments
   WHERE segment = 'VIP';
   \`\`\`

5. **Enable Photon**
   * Ensure Photon is enabled on clusters
   * Use Photon-compatible operations

---

### Issue: Pipeline Runs Too Long

**Symptoms:**
* Bronze/Silver/Gold pipelines take hours
* DBU costs are high

**Solutions:**

1. **Enable Incremental Processing**
   \`\`\`python
   # Ensure streaming tables read only new data
   @dp.table(name="shoplive.silver.customers")
   def silver_customers():
       return spark.readStream.table("shoplive.bronze.customers")
   \`\`\`

2. **Optimize Cluster Size**
   * Right-size worker nodes
   * Use autoscaling
   * Consider spot instances

3. **Reduce Data Scanning**
   \`\`\`sql
   -- Add filters early in query
   SELECT * FROM large_table
   WHERE date_column >= CURRENT_DATE - INTERVAL 7 DAYS
   \`\`\`

4. **Run VACUUM Regularly**
   \`\`\`sql
   VACUUM shoplive.silver.orders RETAIN 168 HOURS;
   \`\`\`

---

## Auto Loader Issues

### Issue: Files Not Being Picked Up

**Symptoms:**
* New files in volume not processed
* Bronze tables not updating

**Solutions:**

1. **Check File Location**
   \`\`\`python
   # Verify files exist
   display(dbutils.fs.ls("/Volumes/shoplive/core/raw/"))
   \`\`\`

2. **Verify pathGlobFilter**
   \`\`\`python
   # Ensure filter matches your files
   df = spark.readStream.format("cloudFiles") \
     .option("cloudFiles.format", "csv") \
     .option("pathGlobFilter", "customers*.csv")  # Check pattern
     .load("/Volumes/shoplive/core/raw/")
   \`\`\`

3. **Check Checkpoint State**
   \`\`\`python
   # List checkpoint files
   display(dbutils.fs.ls("/pipelines/shoplive/bronze/_checkpoints/"))
   \`\`\`

4. **Reset Checkpoint (Last Resort)**
   \`\`\`python
   # WARNING: Will reprocess all data
   dbutils.fs.rm("/pipelines/shoplive/bronze/_checkpoints/customers", True)
   \`\`\`

---

### Issue: Schema Inference Failures

**Symptoms:**
* Error: "Unable to infer schema"
* Auto Loader fails to start

**Solutions:**

1. **Provide Explicit Schema**
   \`\`\`python
   from pyspark.sql.types import StructType, StructField, StringType, DateType
   
   schema = StructType([
       StructField("customer_id", StringType(), False),
       StructField("first_name", StringType(), True),
       StructField("email", StringType(), True),
       StructField("registration_date", DateType(), True)
   ])
   
   df = spark.readStream.format("cloudFiles") \
     .schema(schema) \
     .load("/Volumes/shoplive/core/raw/")
   \`\`\`

2. **Check File Format**
   \`\`\`python
   # Ensure cloudFiles.format matches actual files
   .option("cloudFiles.format", "csv")  # or "json", "parquet", etc.
   \`\`\`

---

## Unity Catalog Issues

### Issue: Permission Denied Errors

**Symptoms:**
* Error: "User does not have permission"
* Cannot read/write tables

**Solutions:**

1. **Check Current Permissions**
   \`\`\`sql
   SHOW GRANTS ON CATALOG shoplive;
   SHOW GRANTS ON SCHEMA shoplive.bronze;
   SHOW GRANTS ON TABLE shoplive.bronze.customers;
   \`\`\`

2. **Grant Required Permissions**
   \`\`\`sql
   -- As catalog admin
   GRANT USE CATALOG ON CATALOG shoplive TO \`user@company.com\`;
   GRANT USE SCHEMA ON SCHEMA shoplive.bronze TO \`user@company.com\`;
   GRANT SELECT ON TABLE shoplive.bronze.customers TO \`user@company.com\`;
   \`\`\`

3. **Check Service Principal**
   * Verify service principal has correct permissions
   * Update IAM roles if using cloud storage

---

### Issue: Volume Not Accessible

**Symptoms:**
* Error: "Volume not found"
* Cannot list files in volume

**Solutions:**

1. **Verify Volume Exists**
   \`\`\`sql
   SHOW VOLUMES IN shoplive.core;
   \`\`\`

2. **Check Volume Permissions**
   \`\`\`sql
   SHOW GRANTS ON VOLUME shoplive.core.raw;
   \`\`\`

3. **Use Correct Path**
   \`\`\`python
   # Correct volume path format
   path = "/Volumes/shoplive/core/raw/"
   # NOT: "/mnt/..." or "dbfs:/Volumes/..."
   \`\`\`

---

## Streaming Issues

### Issue: Streaming Query Stops Unexpectedly

**Symptoms:**
* Stream stops processing
* No error message visible

**Solutions:**

1. **Check Streaming Query Status**
   \`\`\`python
   # In notebook
   for stream in spark.streams.active:
       print(f"ID: {stream.id}, Status: {stream.status}")
   \`\`\`

2. **Review Streaming Metrics**
   \`\`\`python
   stream.lastProgress
   \`\`\`

3. **Increase Trigger Interval**
   \`\`\`python
   # Reduce frequency if system is overloaded
   df.writeStream \
     .trigger(processingTime="10 minutes") \
     .start()
   \`\`\`

---

## General Debugging

### Enable Debug Logging

\`\`\`python
# In notebook
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")

# Enable verbose logging
import logging
logging.getLogger("py4j").setLevel(logging.DEBUG)
\`\`\`

### Check Databricks System Status

Visit: https://status.databricks.com/

### Review Logs

1. **Pipeline Logs**
   * Navigate to pipeline in UI
   * Click "Event Log" tab
   * Review error details

2. **Job Logs**
   * Navigate to job run
   * Click "Logs" tab
   * Check driver/executor logs

3. **Cluster Logs**
   * Navigate to cluster
   * Click "Event Log"
   * Review cluster events

---

## Getting Help

### Internal Resources

* **Slack**: #shoplive-support
* **Email**: data-team@company.com
* **Wiki**: Internal documentation

### External Resources

* [Databricks Documentation](https://docs.databricks.com/)
* [Databricks Community](https://community.databricks.com/)
* [Stack Overflow](https://stackoverflow.com/questions/tagged/databricks)

### Opening a Support Ticket

Include:
* Error message (full stack trace)
* Steps to reproduce
* Pipeline/Job ID
* Cluster configuration
* Data sample (if not sensitive)
* Expected vs. actual behavior

---

## Common Error Messages

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| "Table not found" | Table doesn't exist or no permissions | Verify table exists and check permissions |
| "Column not found" | Schema mismatch | Check schema evolution settings |
| "Permission denied" | Insufficient UC permissions | Grant required permissions |
| "Out of memory" | Cluster too small or data skew | Increase cluster size or repartition data |
| "Stream failed" | Checkpoint issues | Reset checkpoint or fix source data |
| "Schema mismatch" | Schema changed in source | Enable schema evolution |

---

**Last Updated**: 2024-09-11
