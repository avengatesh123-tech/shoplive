# Deployment Guide

This guide provides detailed instructions for deploying the ShopLive E-Commerce Analytics Platform to production.

## Table of Contents

* [Pre-Deployment Checklist](#pre-deployment-checklist)
* [Environment Setup](#environment-setup)
* [Unity Catalog Configuration](#unity-catalog-configuration)
* [Pipeline Deployment](#pipeline-deployment)
* [Job Scheduling](#job-scheduling)
* [Monitoring Setup](#monitoring-setup)
* [Security Configuration](#security-configuration)
* [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Databricks workspace provisioned
- [ ] Unity Catalog enabled
- [ ] AWS S3 buckets created (or equivalent cloud storage)
- [ ] Network connectivity configured
- [ ] IAM roles and permissions set up
- [ ] Compute clusters created

### Access Requirements

- [ ] Admin access to Databricks workspace
- [ ] Unity Catalog admin privileges
- [ ] Cloud provider IAM permissions
- [ ] Git repository access

### Code Readiness

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Version tagged in Git
- [ ] Rollback plan prepared

---

## Environment Setup

### 1. Development Environment

\`\`\`bash
# Catalog and schema names
DEV_CATALOG="shoplive_dev"
DEV_SCHEMAS=("bronze" "silver" "gold" "core")
\`\`\`

### 2. Staging Environment

\`\`\`bash
# Catalog and schema names
STAGING_CATALOG="shoplive_staging"
STAGING_SCHEMAS=("bronze" "silver" "gold" "core")
\`\`\`

### 3. Production Environment

\`\`\`bash
# Catalog and schema names
PROD_CATALOG="shoplive"
PROD_SCHEMAS=("bronze" "silver" "gold" "core")
\`\`\`

---

## Unity Catalog Configuration

### Step 1: Create Catalogs and Schemas

\`\`\`sql
-- Production Catalog
CREATE CATALOG IF NOT EXISTS shoplive
  COMMENT 'ShopLive E-Commerce Analytics - Production';

-- Schemas
CREATE SCHEMA IF NOT EXISTS shoplive.bronze
  COMMENT 'Raw data layer - minimal transformations';

CREATE SCHEMA IF NOT EXISTS shoplive.silver
  COMMENT 'Cleansed and validated data layer';

CREATE SCHEMA IF NOT EXISTS shoplive.gold
  COMMENT 'Business-level aggregations and analytics';

CREATE SCHEMA IF NOT EXISTS shoplive.core
  COMMENT 'Storage, configuration, and utilities';
\`\`\`

### Step 2: Create Volumes

\`\`\`sql
-- Raw data volume
CREATE VOLUME IF NOT EXISTS shoplive.core.raw
  COMMENT 'Raw data storage for Auto Loader ingestion';

-- Checkpoint volume
CREATE VOLUME IF NOT EXISTS shoplive.core.checkpoints
  COMMENT 'Streaming checkpoints for exactly-once processing';
\`\`\`

### Step 3: Set Permissions

\`\`\`sql
-- Grant usage on catalog
GRANT USE CATALOG ON CATALOG shoplive TO \`data-engineers\`;
GRANT USE SCHEMA ON SCHEMA shoplive.bronze TO \`data-engineers\`;
GRANT USE SCHEMA ON SCHEMA shoplive.silver TO \`data-engineers\`;
GRANT USE SCHEMA ON SCHEMA shoplive.gold TO \`data-engineers\`;

-- Grant table permissions
GRANT SELECT ON SCHEMA shoplive.gold TO \`analysts\`;
GRANT MODIFY ON SCHEMA shoplive.bronze TO \`data-engineers\`;
GRANT MODIFY ON SCHEMA shoplive.silver TO \`data-engineers\`;
GRANT MODIFY ON SCHEMA shoplive.gold TO \`data-engineers\`;
\`\`\`

---

## Pipeline Deployment

### Deployment Strategy

We use a **blue-green deployment** approach to minimize downtime:

1. Deploy to "green" environment
2. Run validation tests
3. Switch traffic to "green"
4. Keep "blue" as rollback option

### Step 1: Deploy Code via Databricks UI

1. Navigate to **Workspace** in Databricks UI
2. Create folder: `/production/shoplive/spark/`
3. Import notebooks:
   * Upload `bronze.ipynb` to `/production/shoplive/spark/`
   * Upload `silver.ipynb` to `/production/shoplive/spark/`
   * Upload `gold.ipynb` to `/production/shoplive/spark/`
4. Import transformation scripts:
   * Upload entire `transformations/` folder

### Step 2: Create Pipelines via UI

#### Bronze Pipeline Configuration

1. Navigate to **Workflows** → **Pipelines**
2. Click **Create Pipeline**
3. Configure:
   * **Name**: ShopLive_Bronze_Production
   * **Notebook Path**: `/production/shoplive/spark/bronze`
   * **Target**: `shoplive.bronze`
   * **Storage Location**: `/pipelines/shoplive/bronze`
   * **Pipeline Mode**: Triggered
   * **Photon**: Enabled
   * **Cluster**: Auto-scaling (2-8 workers)

#### Silver Pipeline Configuration

1. Click **Create Pipeline**
2. Configure:
   * **Name**: ShopLive_Silver_Production
   * **Notebook Path**: `/production/shoplive/spark/silver`
   * **Target**: `shoplive.silver`
   * **Storage Location**: `/pipelines/shoplive/silver`
   * **Pipeline Mode**: Triggered

#### Gold Pipeline Configuration

1. Click **Create Pipeline**
2. Configure:
   * **Name**: ShopLive_Gold_Production
   * **Notebook Path**: `/production/shoplive/spark/gold`
   * **Target**: `shoplive.gold`
   * **Storage Location**: `/pipelines/shoplive/gold`
   * **Pipeline Mode**: Triggered

### Step 3: Validate Deployment

\`\`\`sql
-- Check table creation
SHOW TABLES IN shoplive.bronze;
SHOW TABLES IN shoplive.silver;
SHOW TABLES IN shoplive.gold;

-- Validate data quality
SELECT COUNT(*) FROM shoplive.bronze.customers;
SELECT COUNT(*) FROM shoplive.silver.customers;
SELECT COUNT(*) FROM shoplive.gold.customer_segments;

-- Check for null values
SELECT 
  COUNT(*) as total_records,
  COUNT(*) - COUNT(customer_id) as null_ids,
  COUNT(*) - COUNT(email) as null_emails
FROM shoplive.silver.customers;
\`\`\`

---

## Job Scheduling

### Create Orchestration Job via UI

1. Navigate to **Workflows** → **Jobs**
2. Click **Create Job**
3. Configure:
   * **Name**: ShopLive_ETL_Production
   * **Schedule**: Cron `0 2 * * *` (Daily at 2:00 AM UTC)
   * **Max concurrent runs**: 1

4. Add Tasks:

   **Task 1: Bronze Ingestion**
   * Type: Pipeline
   * Pipeline: ShopLive_Bronze_Production
   * Depends on: None

   **Task 2: Silver Cleansing**
   * Type: Pipeline
   * Pipeline: ShopLive_Silver_Production
   * Depends on: Task 1

   **Task 3: Gold Analytics**
   * Type: Pipeline
   * Pipeline: ShopLive_Gold_Production
   * Depends on: Task 2

5. Configure Notifications:
   * On Failure: data-team@company.com
   * On Success: data-team@company.com

### Schedule Options

* **Daily**: `0 2 * * *` (2:00 AM UTC)
* **Hourly**: `0 * * * *` (Every hour)
* **Every 4 hours**: `0 */4 * * *`
* **Weekly**: `0 2 * * 1` (Monday 2:00 AM)

---

## Monitoring Setup

### 1. Pipeline Metrics

\`\`\`sql
-- Monitor pipeline execution
SELECT 
  update_id,
  state,
  creation_time,
  start_time,
  end_time,
  TIMESTAMPDIFF(MINUTE, start_time, end_time) as duration_minutes
FROM system.lakeflow.pipeline_updates
WHERE pipeline_id = '<your_pipeline_id>'
ORDER BY creation_time DESC
LIMIT 10;
\`\`\`

### 2. Data Quality Metrics

\`\`\`sql
-- Track data quality over time
CREATE OR REPLACE TABLE shoplive.core.data_quality_metrics AS
SELECT 
  CURRENT_TIMESTAMP() as check_time,
  'customers' as table_name,
  COUNT(*) as total_records,
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(*) - COUNT(customer_id) as null_ids,
  COUNT(*) - COUNT(email) as null_emails
FROM shoplive.silver.customers;
\`\`\`

### 3. Alert Configuration

Create SQL alerts in Databricks UI:

1. Navigate to **Alerts**
2. Click **Create Alert**
3. Configure:
   * **Name**: ShopLive Data Quality Alert
   * **Query**: Data quality metrics query
   * **Schedule**: Every 6 hours
   * **Conditions**: null_ids > 100 OR null_emails > 100
   * **Notifications**: Email to data-team@company.com

### 4. Cost Monitoring

\`\`\`sql
-- Monitor DBU consumption
SELECT 
  workspace_id,
  sku_name,
  usage_date,
  SUM(usage_quantity) as total_dbus,
  SUM(usage_quantity * list_prices.pricing.default) as estimated_cost
FROM system.billing.usage
WHERE usage_date >= CURRENT_DATE - INTERVAL 30 DAYS
  AND sku_name LIKE '%JOBS%'
GROUP BY workspace_id, sku_name, usage_date
ORDER BY usage_date DESC;
\`\`\`

---

## Security Configuration

### 1. Access Control

\`\`\`sql
-- Restrict production access
GRANT SELECT ON SCHEMA shoplive.gold TO \`analysts\`;
DENY MODIFY ON SCHEMA shoplive.bronze TO \`analysts\`;
DENY MODIFY ON SCHEMA shoplive.silver TO \`analysts\`;
\`\`\`

### 2. Data Masking

\`\`\`sql
-- Mask sensitive data
CREATE OR REPLACE FUNCTION shoplive.core.mask_email(email STRING)
RETURNS STRING
RETURN CONCAT(
  LEFT(email, 2),
  '***@***',
  RIGHT(email, 4)
);
\`\`\`

### 3. Audit Logging

Enable audit logging in Unity Catalog:
* Access logs
* Query logs
* Data modification logs

---

## Rollback Procedures

### Immediate Rollback via UI

1. **Stop Current Pipelines**
   * Navigate to pipeline in Databricks UI
   * Click "Stop" button

2. **Restore Previous Version**
   * Navigate to Workspace
   * Upload backup notebooks
   * Select "Overwrite" option

3. **Restart Pipelines**
   * Navigate to pipeline
   * Click "Start Update"

### Data Rollback Using Delta Time Travel

\`\`\`sql
-- Use Delta Lake time travel
RESTORE TABLE shoplive.gold.customer_segments 
TO VERSION AS OF 100;

-- Or restore to timestamp
RESTORE TABLE shoplive.gold.customer_segments 
TO TIMESTAMP AS OF '2024-09-10T00:00:00';
\`\`\`

---

## Post-Deployment Validation

### Checklist

- [ ] All pipelines running successfully
- [ ] Data quality checks passing
- [ ] No errors in logs
- [ ] Monitoring alerts configured
- [ ] Performance metrics acceptable
- [ ] Stakeholders notified
- [ ] Documentation updated
- [ ] Rollback plan tested

### Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Bronze pipeline duration | < 10 min | |
| Silver pipeline duration | < 15 min | |
| Gold pipeline duration | < 20 min | |
| Total ETL duration | < 60 min | |
| Data quality score | > 99% | |

---

## Troubleshooting

For common deployment issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Support

For deployment issues:
* **Email**: devops@company.com
* **Slack**: #shoplive-deployments
* **Documentation**: Internal wiki
