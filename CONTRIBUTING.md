# Contributing to ShopLive

Thank you for your interest in contributing to the ShopLive E-Commerce Analytics Platform! This document provides guidelines and instructions for contributing.

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [Getting Started](#getting-started)
* [Development Process](#development-process)
* [Coding Standards](#coding-standards)
* [Testing Guidelines](#testing-guidelines)
* [Commit Message Guidelines](#commit-message-guidelines)
* [Pull Request Process](#pull-request-process)
* [Project Structure](#project-structure)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

* Use welcoming and inclusive language
* Be respectful of differing viewpoints and experiences
* Gracefully accept constructive criticism
* Focus on what is best for the community
* Show empathy towards other community members

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Databricks Workspace Access**
   * Unity Catalog enabled
   * DBR 14.3 LTS or higher
   * Appropriate permissions for development

2. **Development Environment**
   * Git for version control
   * Access to the project repository
   * Databricks CLI installed (optional but recommended)

3. **Knowledge Requirements**
   * PySpark fundamentals
   * SQL proficiency
   * Understanding of medallion architecture
   * Delta Lake basics

### Setting Up Your Development Environment

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd shoplive
   \`\`\`

2. **Create a development branch**
   \`\`\`bash
   git checkout -b dev/<your-name>/<feature-name>
   \`\`\`

3. **Set up your Databricks environment**
   * Import the project into your Databricks workspace
   * Create a personal development catalog (e.g., \`shoplive_dev_<your_name>\`)
   * Configure your compute cluster

---

## Development Process

### Branching Strategy

We follow a Git Flow branching model:

* **\`main\`**: Production-ready code
* **\`develop\`**: Integration branch for features
* **\`feature/<name>\`**: New features
* **\`bugfix/<name>\`**: Bug fixes
* **\`hotfix/<name>\`**: Critical production fixes
* **\`release/<version>\`**: Release preparation

### Branch Naming Convention

\`\`\`
feature/add-customer-lifetime-value
bugfix/fix-null-handling-in-silver
hotfix/critical-data-quality-issue
refactor/optimize-bronze-ingestion
docs/update-setup-instructions
\`\`\`

### Development Workflow

1. **Create a feature branch** from \`develop\`
2. **Develop your feature** in isolation
3. **Test thoroughly** in your dev environment
4. **Update documentation** as needed
5. **Submit a pull request** to \`develop\`
6. **Address review feedback**
7. **Merge** after approval

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

#### Formatting
* **Indentation**: 4 spaces (no tabs)
* **Line Length**: Maximum 100 characters
* **Imports**: Group in order: standard library, third-party, local
* **String Quotes**: Double quotes for strings, single for dict keys

#### Example
\`\`\`python
from pyspark import pipelines as dp
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType

@dp.table(
    name="shoplive.silver.customers",
    comment="Cleansed customer data with validation"
)
def silver_customers():
    """
    Transform bronze customer data to silver layer.
    
    Applies:
    - Null handling for required fields
    - Email validation
    - Deduplication by customer_id
    - Standardized country codes
    
    Returns:
        DataFrame: Cleansed customer records
    """
    bronze_df = spark.read.table("shoplive.bronze.customers")
    
    return (
        bronze_df
        .filter(F.col("customer_id").isNotNull())
        .filter(F.col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        .dropDuplicates(["customer_id"])
        .withColumn("country", F.upper(F.col("country")))
    )
\`\`\`

### SQL Style Guide

* **Keywords**: UPPERCASE
* **Identifiers**: lowercase with underscores
* **Indentation**: 2 spaces
* **Comments**: Use \`--\` for inline, \`/* */\` for blocks

#### Example
\`\`\`sql
-- Customer segmentation summary
SELECT 
  segment,
  COUNT(DISTINCT customer_id) AS customer_count,
  ROUND(AVG(monetary), 2) AS avg_lifetime_value,
  ROUND(AVG(frequency), 2) AS avg_order_frequency
FROM shoplive.gold.customer_segments
WHERE segment IN ('VIP', 'Loyal', 'At Risk')
GROUP BY segment
ORDER BY avg_lifetime_value DESC;
\`\`\`

### Documentation Standards

#### Docstrings

Use Google-style docstrings for all functions:

\`\`\`python
def calculate_rfm_score(df, recency_col, frequency_col, monetary_col):
    """
    Calculate RFM scores for customer segmentation.
    
    Args:
        df (DataFrame): Input customer transaction data
        recency_col (str): Column name for recency values
        frequency_col (str): Column name for frequency values
        monetary_col (str): Column name for monetary values
    
    Returns:
        DataFrame: Customer data with RFM scores added
        
    Raises:
        ValueError: If required columns are missing
        
    Example:
        >>> customer_df = calculate_rfm_score(
        ...     transactions_df,
        ...     "days_since_last_order",
        ...     "total_orders",
        ...     "total_spend"
        ... )
    """
    # Implementation here
    pass
\`\`\`

#### Comments

* Write self-explanatory code first
* Add comments for complex business logic
* Explain *why*, not *what*
* Keep comments up-to-date

---

## Testing Guidelines

### Unit Testing

Create unit tests for all transformation logic:

\`\`\`python
# tests/test_transformations.py
import pytest
from pyspark.sql import SparkSession
from transformations.gold.customer_segments import calculate_segment

@pytest.fixture
def spark():
    return SparkSession.builder.master("local[1]").getOrCreate()

def test_vip_customer_segment(spark):
    """Test that customers meeting VIP criteria are classified correctly."""
    # Arrange
    test_data = [
        (1, 10, 20, 100000, None),  # Should be VIP
        (2, 50, 8, 8000, None),     # Should not be VIP
    ]
    df = spark.createDataFrame(
        test_data,
        ["customer_id", "recency", "frequency", "monetary", "segment"]
    )
    
    # Act
    result_df = calculate_segment(df)
    
    # Assert
    vip_customer = result_df.filter("customer_id = 1").collect()[0]
    assert vip_customer.segment == "VIP"
\`\`\`

### Integration Testing

* Test end-to-end pipeline flows
* Verify data quality at each layer
* Validate transformations with sample data

### Testing Checklist

Before submitting a PR, ensure:

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed in dev environment
- [ ] Data quality checks pass
- [ ] No regression in existing functionality
- [ ] Performance impact assessed

---

## Commit Message Guidelines

### Format

\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

### Types

* **feat**: New feature
* **fix**: Bug fix
* **docs**: Documentation changes
* **style**: Code style changes (formatting, no logic change)
* **refactor**: Code refactoring
* **perf**: Performance improvements
* **test**: Adding or updating tests
* **chore**: Maintenance tasks

### Examples

\`\`\`
feat(gold): Add customer lifetime value calculation

Implement CLV calculation using 12-month rolling window.
Includes segmentation by value tier.

Closes #123
\`\`\`

\`\`\`
fix(silver): Handle null values in email validation

Previously null emails caused pipeline failures.
Now filters out records with null emails before validation.

Fixes #456
\`\`\`

---

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest \`develop\`
   \`\`\`bash
   git checkout develop
   git pull origin develop
   git checkout your-feature-branch
   git rebase develop
   \`\`\`

2. **Run all tests** and ensure they pass

3. **Update documentation** if needed

4. **Self-review your code**

### PR Template

When creating a PR, include:

\`\`\`markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #<issue-number>
\`\`\`

### Review Process

* PRs require at least one approval
* Address all review comments
* Keep PRs focused and reasonably sized
* Respond to feedback within 2 business days

---

## Project Structure

### Adding New Transformations

#### Bronze Layer
1. Create \`transformations/bronze/<entity>.py\`
2. Use Auto Loader for data ingestion
3. Minimal transformations only
4. Add to \`bronze.ipynb\`

#### Silver Layer
1. Create \`transformations/silver/<entity>.py\`
2. Implement data quality checks
3. Add business validation
4. Update \`silver.ipynb\`

#### Gold Layer
1. Create \`transformations/gold/<metric>.py\`
2. Implement aggregations
3. Add business logic
4. Update \`gold.ipynb\`

### File Organization

\`\`\`
transformations/
├── bronze/
│   └── new_entity.py          # Raw ingestion
├── silver/
│   └── new_entity.py          # Cleansing
└── gold/
    └── new_metric.py          # Analytics
\`\`\`

---

## Questions?

* **General Questions**: Open a discussion in GitHub Discussions
* **Bug Reports**: Create an issue with the \`bug\` label
* **Feature Requests**: Create an issue with the \`enhancement\` label
* **Security Issues**: Email security@example.com (do not create public issues)

---

## Recognition

Contributors will be recognized in:
* CONTRIBUTORS.md file
* Release notes
* Project documentation

Thank you for contributing to ShopLive! 🎉
