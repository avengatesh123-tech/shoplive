# ShopLive E-Commerce Analytics Platform

[![Databricks](https://img.shields.io/badge/Databricks-Lakehouse-FF3621?logo=databricks)](https://databricks.com)
[![PySpark](https://img.shields.io/badge/PySpark-3.x-E25A1C?logo=apache-spark)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta_Lake-Enabled-00ADD8)](https://delta.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Pipeline Details](#pipeline-details)
- [Analytics & Insights](#analytics--insights)
- [Performance & Optimization](#performance--optimization)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**ShopLive** is a scalable, production-ready e-commerce analytics platform built on the Databricks Lakehouse architecture. It implements a medallion architecture (Bronze → Silver → Gold) to ingest, transform, and analyze e-commerce data for actionable business insights.

### Key Features

✨ **Real-time & Batch Processing**: Support for both streaming and batch data ingestion  
🏗️ **Medallion Architecture**: Bronze, Silver, and Gold layers for data quality and governance  
🔄 **Auto Loader Integration**: Automated, scalable data ingestion from cloud storage  
📊 **Advanced Analytics**: Customer segmentation, product performance, and sales insights  
🎯 **RFM Analysis**: Customer segmentation based on Recency, Frequency, and Monetary value  
⚡ **Delta Lake**: ACID transactions, time travel, and efficient data versioning  
📈 **Incremental Processing**: Optimized for cost-effective, incremental data processing  

---

## 🏛️ Architecture

### Medallion Architecture

The platform follows the medallion architecture pattern with three distinct layers:

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                           │
│                  (CSV Files, Streaming Events)                  │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  🥉 BRONZE LAYER (shoplive.bronze)                              │
│  • Raw data ingestion via Auto Loader                           │
│  • Schema inference and validation                              │
│  • Minimal transformations                                      │
│  Tables: customers, orders, products, events                    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  🥈 SILVER LAYER (shoplive.silver)                              │
│  • Data cleansing and standardization                           │
│  • Deduplication and quality checks                             │
│  • Business logic application                                   │
│  Tables: customers, orders, products, events                    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  🥇 GOLD LAYER (shoplive.gold)                                  │
│  • Aggregated business metrics                                  │
│  • Customer segmentation (RFM)                                  │
│  • Product and category performance                             │
│  • Analytics-ready data                                         │
│  Tables: customer_segments, product_performance,                │
│          category_performance, daily_category_sales, etc.       │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICS & BI TOOLS                         │
│              (Dashboards, Reports, ML Models)                   │
└─────────────────────────────────────────────────────────────────┘
\`\`\`

### Technology Stack

- **Platform**: Databricks on AWS
- **Processing Engine**: Apache Spark (PySpark)
- **Storage Layer**: Delta Lake
- **Orchestration**: Databricks Workflows / Jobs
- **Data Ingestion**: Auto Loader (CloudFiles)
- **Languages**: Python, SQL
- **Unity Catalog**: Unified governance and metadata management

---

## 📁 Project Structure

\`\`\`
shoplive/
├── README.md                          # This file
├── data/                              # Data generation and ingestion
│   ├── batch_data/
│   │   └── batch_data_generator.ipynb # Batch data generation notebook
│   └── stream/
│       └── stream_data.ipynb          # Streaming data generation notebook
│
├── spark/                             # Spark processing pipelines
│   ├── bronze.ipynb                   # Bronze layer pipeline
│   ├── silver.ipynb                   # Silver layer pipeline
│   ├── gold.ipynb                     # Gold layer pipeline
│   │
│   └── transformations/               # Modular transformation scripts
│       ├── bronze/                    # Bronze layer transformations
│       │   ├── customers.py           # Customer raw data ingestion
│       │   ├── orders.py              # Order raw data ingestion
│       │   ├── products.py            # Product raw data ingestion
│       │   └── events.py              # Event raw data ingestion
│       │
│       ├── silver/                    # Silver layer transformations
│       │   ├── customers.py           # Customer data cleansing
│       │   ├── orders.py              # Order data cleansing
│       │   ├── products.py            # Product data cleansing
│       │   └── events.py              # Event data cleansing
│       │
│       └── gold/                      # Gold layer transformations
│           ├── customer_segments.py       # RFM customer segmentation
│           ├── customers.py               # Customer analytics
│           ├── product_performance.py     # Product performance metrics
│           ├── category_performance.py    # Category performance metrics
│           ├── daily_category_sales.py    # Daily sales by category
│           ├── orders_products.py         # Order-product relationships
│           └── order_status_summary.py    # Order status aggregations
│
└── .git/                              # Git version control
\`\`\`

---

## 📊 Data Model

### Bronze Layer Tables

#### \`shoplive.bronze.customers\`
Raw customer data ingested from source systems.

| Column | Type | Description |
|--------|------|-------------|
| customer_id | STRING | Unique customer identifier |
| first_name | STRING | Customer first name |
| last_name | STRING | Customer last name |
| email | STRING | Customer email address |
| registration_date | DATE | Account registration date |
| country | STRING | Customer country |

#### \`shoplive.bronze.orders\`
Raw order transactions.

| Column | Type | Description |
|--------|------|-------------|
| order_id | STRING | Unique order identifier |
| customer_id | STRING | Customer identifier (FK) |
| product_id | STRING | Product identifier (FK) |
| order_date | TIMESTAMP | Order timestamp |
| quantity | INTEGER | Quantity ordered |
| unit_price | DECIMAL | Price per unit |
| status | STRING | Order status |

#### \`shoplive.bronze.products\`
Raw product catalog data.

| Column | Type | Description |
|--------|------|-------------|
| product_id | STRING | Unique product identifier |
| product_name | STRING | Product name |
| category | STRING | Product category |
| price | DECIMAL | Product price |
| stock_quantity | INTEGER | Available stock |

#### \`shoplive.bronze.events\`
Raw event tracking data (page views, clicks, etc.).

| Column | Type | Description |
|--------|------|-------------|
| event_id | STRING | Unique event identifier |
| customer_id | STRING | Customer identifier |
| event_type | STRING | Type of event |
| event_timestamp | TIMESTAMP | Event timestamp |
| product_id | STRING | Related product (if applicable) |

### Silver Layer Tables

Cleansed and standardized versions of Bronze tables with:
- Null value handling
- Data type conversions
- Duplicate removal
- Business rule validation
- Data quality constraints

### Gold Layer Tables

#### \`shoplive.gold.customer_segments\`
RFM-based customer segmentation.

| Column | Type | Description |
|--------|------|-------------|
| customer_id | STRING | Customer identifier |
| recency | INTEGER | Days since last purchase |
| frequency | INTEGER | Total number of orders |
| monetary | DECIMAL | Total lifetime value |
| segment | STRING | Customer segment (VIP, Loyal, At Risk, Churned, New) |

**Segmentation Rules:**
- **VIP**: Recency ≤ 30 days, Frequency ≥ 10, Monetary ≥ $50,000
- **Loyal**: Recency ≤ 30 days, Frequency ≥ 5, Monetary ≥ $10,000
- **At Risk**: 30 < Recency ≤ 90 days, Frequency ≥ 3
- **Churned**: Recency > 90 days
- **New**: All others

#### \`shoplive.gold.product_performance\`
Product-level performance metrics.

| Column | Type | Description |
|--------|------|-------------|
| product_id | STRING | Product identifier |
| product_name | STRING | Product name |
| category | STRING | Product category |
| total_orders | INTEGER | Total orders |
| total_quantity_sold | INTEGER | Units sold |
| total_revenue | DECIMAL | Total revenue generated |
| avg_order_value | DECIMAL | Average order value |

#### \`shoplive.gold.category_performance\`
Category-level performance metrics.

#### \`shoplive.gold.daily_category_sales\`
Daily sales trends by category.

#### \`shoplive.gold.order_status_summary\`
Order status distribution and metrics.

---

## ⚙️ Prerequisites

### Required

- **Databricks Workspace** (AWS, Azure, or GCP)
- **Unity Catalog** enabled
- **Databricks Runtime** 13.0+ (recommended: 14.3 LTS)
- **Cluster Configuration**:
  - Runtime: DBR 14.3 LTS or later
  - Node Type: i3.xlarge or equivalent (for production)
  - Auto Scaling: Enabled
  - Photon: Enabled (recommended)

### Permissions

- \`CREATE TABLE\` on the \`shoplive\` catalog
- \`USE CATALOG\` and \`USE SCHEMA\` permissions
- Read/Write access to Unity Catalog volumes: \`/Volumes/shoplive/core/raw/\`
- Execute permissions on notebooks and pipelines

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

\`\`\`bash
# If using Databricks Repos
# Navigate to Repos in your Databricks workspace
# Click "Add Repo" and provide the Git repository URL
\`\`\`

Or manually upload the project to your Databricks workspace:
\`\`\`bash
# Use Databricks CLI
databricks workspace import_dir ./shoplive /Workspace/db_project/shoplive
\`\`\`

### Step 2: Create Unity Catalog Resources

\`\`\`sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS shoplive;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS shoplive.bronze
  COMMENT 'Raw data layer - minimal transformations';

CREATE SCHEMA IF NOT EXISTS shoplive.silver
  COMMENT 'Cleansed and validated data layer';

CREATE SCHEMA IF NOT EXISTS shoplive.gold
  COMMENT 'Business-level aggregations and analytics';

CREATE SCHEMA IF NOT EXISTS shoplive.core
  COMMENT 'Storage and configuration';

-- Create volume for raw data
CREATE VOLUME IF NOT EXISTS shoplive.core.raw
  COMMENT 'Raw data storage for Auto Loader ingestion';
\`\`\`

### Step 3: Configure Data Generation

1. Open \`data/batch_data/batch_data_generator.ipynb\`
2. Run all cells to generate sample batch data
3. Open \`data/stream/stream_data.ipynb\`
4. Configure streaming data generation parameters
5. Run to start generating streaming events

### Step 4: Set Up Pipelines

Create a Databricks pipeline for each layer:

#### Bronze Pipeline
\`\`\`python
# Configuration
Pipeline Name: ShopLive Bronze Ingestion
Notebook Path: /db_project/shoplive/spark/bronze.ipynb
Target: shoplive.bronze
Storage Location: dbfs:/pipelines/shoplive/bronze
Pipeline Mode: Triggered or Continuous
\`\`\`

#### Silver Pipeline
\`\`\`python
# Configuration
Pipeline Name: ShopLive Silver Cleansing
Notebook Path: /db_project/shoplive/spark/silver.ipynb
Target: shoplive.silver
Storage Location: dbfs:/pipelines/shoplive/silver
Pipeline Mode: Triggered
\`\`\`

#### Gold Pipeline
\`\`\`python
# Configuration
Pipeline Name: ShopLive Gold Analytics
Notebook Path: /db_project/shoplive/spark/gold.ipynb
Target: shoplive.gold
Storage Location: dbfs:/pipelines/shoplive/gold
Pipeline Mode: Triggered
\`\`\`

### Step 5: Schedule Pipeline Execution

Create a Databricks Job to orchestrate the pipelines:

\`\`\`yaml
Job Name: ShopLive ETL Pipeline
Tasks:
  - Task 1: Bronze Pipeline (Depends on: None)
  - Task 2: Silver Pipeline (Depends on: Task 1)
  - Task 3: Gold Pipeline (Depends on: Task 2)
Schedule: Daily at 2:00 AM UTC
Retry Policy: 3 retries with 5-minute intervals
Notifications: Email on failure
\`\`\`

---

## 💻 Usage

### Running Individual Pipelines

#### Bronze Layer (Data Ingestion)
\`\`\`python
# Open spark/bronze.ipynb
# This notebook ingests raw data from /Volumes/shoplive/core/raw/
# Auto Loader automatically detects new files and processes incrementally
\`\`\`

#### Silver Layer (Data Cleansing)
\`\`\`python
# Open spark/silver.ipynb
# This notebook cleanses and validates data from bronze tables
# Applies business rules and data quality checks
\`\`\`

#### Gold Layer (Analytics)
\`\`\`python
# Open spark/gold.ipynb
# This notebook creates aggregated analytics tables
# Generates customer segments, product performance metrics, etc.
\`\`\`

### Querying Analytics Tables

\`\`\`sql
-- Customer Segmentation
SELECT 
  segment,
  COUNT(*) as customer_count,
  ROUND(AVG(monetary), 2) as avg_lifetime_value,
  ROUND(AVG(frequency), 2) as avg_order_frequency
FROM shoplive.gold.customer_segments
GROUP BY segment
ORDER BY avg_lifetime_value DESC;

-- Top Performing Products
SELECT 
  product_name,
  category,
  total_revenue,
  total_quantity_sold,
  avg_order_value
FROM shoplive.gold.product_performance
ORDER BY total_revenue DESC
LIMIT 10;

-- Daily Sales Trend
SELECT 
  sale_date,
  category,
  total_sales,
  total_orders
FROM shoplive.gold.daily_category_sales
WHERE sale_date >= CURRENT_DATE - INTERVAL 30 DAYS
ORDER BY sale_date DESC, total_sales DESC;
\`\`\`

---

## 🔄 Pipeline Details

### Bronze Layer

**Purpose**: Ingest raw data with minimal transformations

**Key Features**:
- **Auto Loader**: Automatically detects and processes new files
- **Schema Inference**: Automatically infers column types
- **Incremental Processing**: Only processes new/changed data
- **Streaming Support**: Real-time data ingestion

**Transformation Files**:
- \`bronze/customers.py\`: Ingests customer CSV files
- \`bronze/orders.py\`: Ingests order transaction files
- \`bronze/products.py\`: Ingests product catalog files
- \`bronze/events.py\`: Ingests event tracking data

### Silver Layer

**Purpose**: Cleanse, validate, and standardize data

**Key Features**:
- **Data Quality Checks**: Null handling, type validation
- **Deduplication**: Remove duplicate records
- **Standardization**: Consistent formatting and naming
- **Referential Integrity**: Validate foreign key relationships

**Transformation Files**:
- \`silver/customers.py\`: Customer data cleansing and enrichment
- \`silver/orders.py\`: Order data validation and standardization
- \`silver/products.py\`: Product data quality checks
- \`silver/events.py\`: Event data cleansing

### Gold Layer

**Purpose**: Create business-level aggregations and analytics

**Key Features**:
- **Customer Segmentation**: RFM analysis for targeted marketing
- **Product Analytics**: Performance metrics and trends
- **Category Analysis**: Category-level insights
- **Materialized Views**: Pre-aggregated for fast query performance

**Transformation Files**:
- \`gold/customer_segments.py\`: RFM-based customer segmentation
- \`gold/product_performance.py\`: Product-level KPIs
- \`gold/category_performance.py\`: Category-level metrics
- \`gold/daily_category_sales.py\`: Time-series sales data
- \`gold/order_status_summary.py\`: Order fulfillment metrics

---

## 📈 Analytics & Insights

### Customer Segmentation (RFM Analysis)

The platform implements RFM (Recency, Frequency, Monetary) analysis to segment customers:

- **Recency**: Days since last purchase
- **Frequency**: Total number of orders
- **Monetary**: Total customer lifetime value

**Use Cases**:
- **VIP Customers**: Target with exclusive offers and premium support
- **Loyal Customers**: Reward with loyalty programs
- **At Risk**: Re-engagement campaigns to prevent churn
- **Churned**: Win-back campaigns and special offers
- **New**: Onboarding and welcome campaigns

### Product Performance

Track key product metrics:
- Total revenue per product
- Units sold
- Average order value
- Sales velocity
- Stock turnover

### Category Performance

Analyze category-level trends:
- Revenue by category
- Market share
- Growth rates
- Seasonal patterns

---

## ⚡ Performance & Optimization

### Best Practices Implemented

1. **Delta Lake Optimization**
   \`\`\`sql
   -- Run OPTIMIZE regularly on frequently queried tables
   OPTIMIZE shoplive.gold.customer_segments;
   OPTIMIZE shoplive.gold.product_performance ZORDER BY (category, product_id);
   \`\`\`

2. **Auto Loader Checkpointing**
   - Tracks processed files to avoid reprocessing
   - Enables exactly-once processing guarantees

3. **Incremental Processing**
   - Only processes new or changed data
   - Reduces compute costs and processing time

4. **Partitioning Strategy**
   \`\`\`sql
   -- Partition large tables by date for efficient queries
   CREATE TABLE shoplive.silver.orders
   PARTITIONED BY (order_date)
   \`\`\`

5. **Caching Strategy**
   - Cache frequently accessed dimension tables
   - Use broadcast joins for small lookup tables

### Monitoring & Observability

- **Pipeline Metrics**: Monitor pipeline execution time and data quality
- **Data Quality Checks**: Track null rates, duplicate counts, schema changes
- **Cost Monitoring**: Track DBU consumption per pipeline
- **Alert Configuration**: Set up alerts for pipeline failures or data quality issues

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**
   \`\`\`bash
   git checkout -b feature/your-feature-name
   \`\`\`
3. **Commit your changes**
   \`\`\`bash
   git commit -m "Add: description of your changes"
   \`\`\`
4. **Push to the branch**
   \`\`\`bash
   git push origin feature/your-feature-name
   \`\`\`
5. **Open a Pull Request**

### Code Standards

- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation for any changes
- Ensure all pipelines run successfully

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/your-org/shoplive/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/shoplive/discussions)
- **Email**: your-email@example.com

---

## 🙏 Acknowledgments

- Built on the [Databricks Lakehouse Platform](https://databricks.com)
- Powered by [Apache Spark](https://spark.apache.org/) and [Delta Lake](https://delta.io/)
- Inspired by the [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) pattern

---

## 📚 Additional Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/)
- [Auto Loader Guide](https://docs.databricks.com/ingestion/auto-loader/)
- [Medallion Architecture Best Practices](https://www.databricks.com/glossary/medallion-architecture)

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Databricks Runtime**: 14.3 LTS+

---

*Built with ❤️ on Databricks*
