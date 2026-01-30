# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Deployment Setup & Environment Configuration
# MAGIC 
# MAGIC ## Overview
# MAGIC This notebook automates the deployment setup for the Payment Authorization demo. Run this notebook **first** before executing any other notebooks.
# MAGIC 
# MAGIC **What this notebook does:**
# MAGIC - Creates Unity Catalog structure (catalog, schemas)
# MAGIC - Creates required directories in DBFS
# MAGIC - Uploads configuration files
# MAGIC - Validates environment setup
# MAGIC - Creates checkpoint locations
# MAGIC - Sets up MLflow experiment
# MAGIC - Provides cluster configuration recommendations
# MAGIC 
# MAGIC **Prerequisites:**
# MAGIC - Databricks workspace (Premium or Enterprise tier)
# MAGIC - Unity Catalog enabled
# MAGIC - Permissions: CREATE CATALOG, CREATE SCHEMA, CREATE TABLE, MODIFY
# MAGIC 
# MAGIC **Estimated time:** 5 minutes

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Import Required Libraries

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
import json
import os
from datetime import datetime

# Display setup information
print("=" * 80)
print("PAYMENT AUTHORIZATION DEMO - DEPLOYMENT SETUP")
print("=" * 80)
print(f"Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
print(f"User: {spark.conf.get('spark.databricks.clusterUsageTags.clusterOwnerOrgId')}")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Configuration Parameters
# MAGIC 
# MAGIC **Modify these parameters if needed:**

# COMMAND ----------

# Catalog and schema names
CATALOG_NAME = "payments_lakehouse"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

# DBFS paths
BASE_PATH = "/dbfs/payments_demo"
CONFIG_PATH = f"{BASE_PATH}/config"
DATA_PATH = f"{BASE_PATH}/data"
CHECKPOINT_PATH = f"{BASE_PATH}/checkpoints"

# Delta table paths
DELTA_BASE = "dbfs:/payments_demo"
DELTA_BRONZE = f"{DELTA_BASE}/bronze"
DELTA_SILVER = f"{DELTA_BASE}/silver"
DELTA_GOLD = f"{DELTA_BASE}/gold"

# MLflow experiment path
MLFLOW_EXPERIMENT_PATH = "/Shared/payment_authorization_demo"

print("✅ Configuration loaded:")
print(f"   Catalog: {CATALOG_NAME}")
print(f"   Schemas: {SCHEMA_BRONZE}, {SCHEMA_SILVER}, {SCHEMA_GOLD}")
print(f"   Base Path: {BASE_PATH}")
print(f"   MLflow Experiment: {MLFLOW_EXPERIMENT_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Directory Structure

# COMMAND ----------

# Create directories
directories = [
    BASE_PATH,
    CONFIG_PATH,
    DATA_PATH,
    CHECKPOINT_PATH,
    f"{CHECKPOINT_PATH}/transactions_raw",
    f"{CHECKPOINT_PATH}/payments_enriched_stream",
    f"{CHECKPOINT_PATH}/smart_retry_recommendations"
]

print("Creating directory structure...")
for directory in directories:
    try:
        dbutils.fs.mkdirs(directory.replace("/dbfs", "dbfs:"))
        print(f"✅ Created: {directory}")
    except Exception as e:
        print(f"⚠️  Directory may already exist: {directory}")

print("\n✅ Directory structure created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Unity Catalog Structure

# COMMAND ----------

# Create catalog
print(f"Creating catalog: {CATALOG_NAME}")
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG_NAME}")
    print(f"✅ Catalog '{CATALOG_NAME}' created successfully")
except Exception as e:
    print(f"⚠️  Catalog creation warning: {e}")

# Set current catalog
spark.sql(f"USE CATALOG {CATALOG_NAME}")
print(f"✅ Using catalog: {CATALOG_NAME}")

# Create schemas
schemas = [SCHEMA_BRONZE, SCHEMA_SILVER, SCHEMA_GOLD]
for schema in schemas:
    try:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"✅ Schema '{schema}' created successfully")
    except Exception as e:
        print(f"⚠️  Schema creation warning: {e}")

# Add catalog comment
try:
    spark.sql(f"""
    COMMENT ON CATALOG {CATALOG_NAME} IS 
    'Payment authorization optimization demo: Smart Checkout, Reason Code Analytics, Smart Retry. Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    """)
    print("✅ Catalog comment added")
except Exception as e:
    print(f"⚠️  Comment addition warning: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Upload Configuration Files
# MAGIC 
# MAGIC **Note:** Configuration files should be uploaded manually via Databricks UI or REST API, or you can create them here.

# COMMAND ----------

# Create routing_policies.json
routing_policies = {
    "payment_solutions": {
        "3DS": {
            "description": "3D Secure authentication",
            "mandatory_regions": ["EU", "UK", "IN"],
            "risk_reduction": 0.35,
            "approval_impact": -0.08,
            "cost_per_transaction": 0.15
        },
        "Antifraud": {
            "description": "Real-time fraud scoring",
            "mandatory_regions": [],
            "risk_reduction": 0.45,
            "approval_impact": -0.05,
            "cost_per_transaction": 0.10
        },
        "IDPay": {
            "description": "Identity verification",
            "mandatory_regions": [],
            "risk_reduction": 0.25,
            "approval_impact": 0.03,
            "cost_per_transaction": 0.20
        },
        "DataShareOnly": {
            "description": "Minimal data sharing",
            "mandatory_regions": [],
            "risk_reduction": 0.10,
            "approval_impact": 0.08,
            "cost_per_transaction": 0.05
        },
        "NetworkToken": {
            "description": "Network tokenization",
            "mandatory_regions": [],
            "risk_reduction": 0.20,
            "approval_impact": 0.12,
            "cost_per_transaction": 0.08
        },
        "Passkey": {
            "description": "Biometric authentication",
            "mandatory_regions": [],
            "risk_reduction": 0.40,
            "approval_impact": 0.05,
            "cost_per_transaction": 0.12
        }
    },
    "cascading_rules": {
        "decline_code_mappings": {
            "05_DO_NOT_HONOR": {
                "cascade_options": ["NetworkToken+3DS", "Passkey+Antifraud"],
                "wait_time_seconds": 300
            },
            "51_INSUFFICIENT_FUNDS": {
                "cascade_options": ["SmartRetry"],
                "wait_time_seconds": 86400
            },
            "61_EXCEEDS_LIMIT": {
                "cascade_options": ["NetworkToken+DataShareOnly"],
                "wait_time_seconds": 600
            },
            "63_SECURITY_VIOLATION": {
                "cascade_options": ["3DS+Antifraud+IDPay"],
                "wait_time_seconds": 3600
            }
        }
    },
    "risk_thresholds": {
        "low_risk": {"max_score": 0.3, "recommended_solutions": ["DataShareOnly"]},
        "medium_risk": {"max_score": 0.6, "recommended_solutions": ["Antifraud", "NetworkToken"]},
        "high_risk": {"max_score": 0.85, "recommended_solutions": ["3DS", "Antifraud", "IDPay"]},
        "critical_risk": {"max_score": 1.0, "recommended_solutions": ["3DS", "Antifraud", "IDPay", "Passkey"]}
    }
}

# Write to DBFS
with open(f"{CONFIG_PATH}/routing_policies.json", "w") as f:
    json.dump(routing_policies, f, indent=2)
print("✅ Created routing_policies.json")

# COMMAND ----------

# Create retry_policies.json
retry_policies = {
    "retry_strategies": {
        "recurring_payments": {
            "max_attempts": 5,
            "backoff_schedule": [1, 3, 7, 14, 30],
            "optimal_retry_windows": {
                "salary_days": [1, 2, 15, 16],
                "business_hours": {"start": 9, "end": 17}
            }
        },
        "cardholder_initiated": {
            "max_attempts": 3,
            "backoff_schedule": [0, 1, 3],
            "immediate_retry_threshold": 0.7
        }
    },
    "decline_code_retry_rules": {
        "05_DO_NOT_HONOR": {"retry_allowed": True, "min_wait_hours": 1, "success_probability_threshold": 0.35},
        "51_INSUFFICIENT_FUNDS": {"retry_allowed": True, "min_wait_hours": 24, "success_probability_threshold": 0.50, "prefer_salary_days": True},
        "54_EXPIRED_CARD": {"retry_allowed": False, "min_wait_hours": None, "success_probability_threshold": 0.0},
        "61_EXCEEDS_LIMIT": {"retry_allowed": True, "min_wait_hours": 6, "success_probability_threshold": 0.40},
        "91_ISSUER_UNAVAILABLE": {"retry_allowed": True, "min_wait_hours": 0.5, "success_probability_threshold": 0.60}
    },
    "ml_model_config": {
        "model_name": "smart_retry_classifier",
        "version": "1.0.0",
        "features": [
            "time_since_last_attempt_hours", "num_prior_attempts", "last_reason_code_numeric",
            "issuer_success_rate_7d", "cardholder_risk_score", "merchant_risk_score",
            "is_salary_day", "is_business_hours", "day_of_week", "transaction_amount_log",
            "sector_risk_score", "country_risk_score"
        ],
        "min_approval_probability": 0.30,
        "max_risk_score": 0.75
    }
}

with open(f"{CONFIG_PATH}/retry_policies.json", "w") as f:
    json.dump(retry_policies, f, indent=2)
print("✅ Created retry_policies.json")

# COMMAND ----------

# Create reason_codes.json
reason_codes = {
    "reason_code_taxonomy": {
        "00_APPROVED": {"category": "Approved", "severity": "none", "actionable": False, "description": "Transaction approved"},
        "05_DO_NOT_HONOR": {
            "category": "Soft Decline", "severity": "medium", "actionable": True,
            "description": "Generic decline by issuer",
            "root_causes": ["Risk scoring threshold", "Velocity controls"],
            "recommended_actions": ["Enable 3DS authentication", "Use Network Tokenization"]
        },
        "51_INSUFFICIENT_FUNDS": {
            "category": "Soft Decline", "severity": "low", "actionable": True,
            "description": "Not enough funds in account",
            "root_causes": ["Account balance low"],
            "recommended_actions": ["Retry after salary days (1st, 15th)", "Offer installment payment"]
        },
        "61_EXCEEDS_LIMIT": {
            "category": "Soft Decline", "severity": "medium", "actionable": True,
            "description": "Transaction amount exceeds limit",
            "root_causes": ["Single transaction limit", "Daily spending limit"],
            "recommended_actions": ["Split transaction into smaller amounts", "Request limit increase"]
        },
        "63_SECURITY_VIOLATION": {
            "category": "Hard Decline", "severity": "critical", "actionable": True,
            "description": "Security code mismatch or fraud suspected",
            "root_causes": ["CVV mismatch", "Fraud scoring threshold"],
            "recommended_actions": ["Enable 3DS + Antifraud + IDPay", "Use biometric authentication"]
        },
        "91_ISSUER_UNAVAILABLE": {
            "category": "Technical", "severity": "medium", "actionable": True,
            "description": "Issuer system timeout or unavailable",
            "root_causes": ["Issuer system downtime", "Network timeout"],
            "recommended_actions": ["Immediate retry (30-60 seconds)", "Route through alternative acquirer"]
        }
    }
}

with open(f"{CONFIG_PATH}/reason_codes.json", "w") as f:
    json.dump(reason_codes, f, indent=2)
print("✅ Created reason_codes.json")

print("\n✅ All configuration files created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Verify Configuration Files

# COMMAND ----------

# List configuration files
print("Configuration files in DBFS:")
config_files = dbutils.fs.ls(CONFIG_PATH.replace("/dbfs", "dbfs:"))
for file in config_files:
    print(f"  ✅ {file.name} ({file.size} bytes)")

# Verify JSON validity
print("\nVerifying JSON files:")
for file in ["routing_policies.json", "retry_policies.json", "reason_codes.json"]:
    try:
        with open(f"{CONFIG_PATH}/{file}", "r") as f:
            json.load(f)
        print(f"  ✅ {file} - Valid JSON")
    except Exception as e:
        print(f"  ❌ {file} - Invalid JSON: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Create MLflow Experiment

# COMMAND ----------

import mlflow

# Create MLflow experiment
try:
    mlflow.set_experiment(MLFLOW_EXPERIMENT_PATH)
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_PATH)
    print(f"✅ MLflow experiment created/found:")
    print(f"   Name: {experiment.name}")
    print(f"   Experiment ID: {experiment.experiment_id}")
    print(f"   Artifact Location: {experiment.artifact_location}")
except Exception as e:
    print(f"⚠️  MLflow experiment warning: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Environment Validation

# COMMAND ----------

print("=" * 80)
print("ENVIRONMENT VALIDATION")
print("=" * 80)

validation_passed = True

# Check 1: Unity Catalog
print("\n1. Unity Catalog Check:")
try:
    catalogs = spark.sql("SHOW CATALOGS").collect()
    catalog_names = [row.catalog for row in catalogs]
    if CATALOG_NAME in catalog_names:
        print(f"   ✅ Catalog '{CATALOG_NAME}' exists")
    else:
        print(f"   ❌ Catalog '{CATALOG_NAME}' not found")
        validation_passed = False
except Exception as e:
    print(f"   ❌ Error checking catalogs: {e}")
    validation_passed = False

# Check 2: Schemas
print("\n2. Schema Check:")
try:
    spark.sql(f"USE CATALOG {CATALOG_NAME}")
    schemas = spark.sql("SHOW SCHEMAS").collect()
    schema_names = [row.databaseName for row in schemas]
    for schema in [SCHEMA_BRONZE, SCHEMA_SILVER, SCHEMA_GOLD]:
        if schema in schema_names:
            print(f"   ✅ Schema '{schema}' exists")
        else:
            print(f"   ❌ Schema '{schema}' not found")
            validation_passed = False
except Exception as e:
    print(f"   ❌ Error checking schemas: {e}")
    validation_passed = False

# Check 3: DBFS directories
print("\n3. DBFS Directory Check:")
for directory in [BASE_PATH, CONFIG_PATH, CHECKPOINT_PATH]:
    try:
        dbutils.fs.ls(directory.replace("/dbfs", "dbfs:"))
        print(f"   ✅ {directory} exists")
    except Exception as e:
        print(f"   ❌ {directory} not accessible: {e}")
        validation_passed = False

# Check 4: Configuration files
print("\n4. Configuration File Check:")
for file in ["routing_policies.json", "retry_policies.json", "reason_codes.json"]:
    try:
        with open(f"{CONFIG_PATH}/{file}", "r") as f:
            json.load(f)
        print(f"   ✅ {file} is valid")
    except Exception as e:
        print(f"   ❌ {file} error: {e}")
        validation_passed = False

# Check 5: MLflow
print("\n5. MLflow Check:")
try:
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_PATH)
    if experiment:
        print(f"   ✅ MLflow experiment exists")
    else:
        print(f"   ❌ MLflow experiment not found")
        validation_passed = False
except Exception as e:
    print(f"   ❌ MLflow error: {e}")
    validation_passed = False

# Check 6: Spark version
print("\n6. Databricks Runtime Check:")
try:
    runtime = spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')
    print(f"   ✅ Runtime: {runtime}")
    if "14." in runtime or "13." in runtime:
        print(f"   ✅ Runtime version is compatible")
    else:
        print(f"   ⚠️  Recommended: Databricks Runtime 13.3 LTS or 14.3 LTS")
except Exception as e:
    print(f"   ⚠️  Cannot determine runtime: {e}")

print("\n" + "=" * 80)
if validation_passed:
    print("✅ ALL VALIDATION CHECKS PASSED")
    print("=" * 80)
    print("\n🎉 Environment setup is complete!")
    print("\nNext steps:")
    print("  1. Run notebook: 01_ingest_synthetic_data")
    print("  2. Run notebook: 02_stream_enrichment_smart_checkout")
    print("  3. Run notebook: 03_reason_code_performance")
    print("  4. Run notebook: 04_smart_retry")
    print("  5. Run notebook: 05_dashboards_and_genie_examples")
    print("  6. Run notebook: 06_app_demo_ui")
else:
    print("❌ SOME VALIDATION CHECKS FAILED")
    print("=" * 80)
    print("\n⚠️  Please review the errors above and fix before proceeding")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9: Cluster Configuration Recommendations

# COMMAND ----------

print("=" * 80)
print("RECOMMENDED CLUSTER CONFIGURATION")
print("=" * 80)
print("""
For optimal performance, configure your cluster with:

**Driver Node:**
- Instance Type: Standard_DS3_v2 or larger
- Memory: 14 GB minimum
- Cores: 4 minimum

**Worker Nodes:**
- Min Workers: 2
- Max Workers: 8 (for auto-scaling)
- Instance Type: Standard_DS3_v2 or larger

**Databricks Runtime:**
- Version: 14.3 LTS or 13.3 LTS
- ML Runtime: Optional (for notebook 04 - Smart Retry)

**Libraries:**
- Pre-installed: pyspark, pandas, mlflow, plotly
- Additional: streamlit (for notebook 06 - Databricks App)

**Auto-scaling:**
- Enable auto-scaling for cost optimization
- Min: 2 workers, Max: 8 workers

**Auto-termination:**
- Set to 30 minutes for development
- Disable for production streaming jobs

To install additional libraries:
  %pip install streamlit plotly

""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10: Generate Setup Summary Report

# COMMAND ----------

# Generate summary report
summary = f"""
{'=' * 80}
PAYMENT AUTHORIZATION DEMO - SETUP SUMMARY
{'=' * 80}

Setup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

UNITY CATALOG:
  - Catalog: {CATALOG_NAME}
  - Schemas: {SCHEMA_BRONZE}, {SCHEMA_SILVER}, {SCHEMA_GOLD}

DBFS PATHS:
  - Base: {BASE_PATH}
  - Config: {CONFIG_PATH}
  - Data: {DATA_PATH}
  - Checkpoints: {CHECKPOINT_PATH}

CONFIGURATION FILES:
  ✅ routing_policies.json
  ✅ retry_policies.json
  ✅ reason_codes.json

MLFLOW:
  - Experiment: {MLFLOW_EXPERIMENT_PATH}

NEXT STEPS:
  1. Verify all validation checks passed above
  2. Run notebooks 01-06 in sequence
  3. Monitor streaming jobs in Spark UI
  4. Deploy Databricks App for live monitoring

DOCUMENTATION:
  - QUICKSTART.md - 30-minute setup guide
  - README.md - Complete documentation
  - DEPLOYMENT.md - Production deployment guide
  - DEMO_SCRIPT.md - Presentation walkthrough

SUPPORT:
  - GitHub: https://github.com/arielhsaa/accelerate_approvals_demo
  - Issues: Report via GitHub Issues

{'=' * 80}
✅ SETUP COMPLETE - READY TO RUN DEMO NOTEBOOKS
{'=' * 80}
"""

print(summary)

# Save summary to DBFS
with open(f"{BASE_PATH}/setup_summary.txt", "w") as f:
    f.write(summary)

print(f"\n📄 Setup summary saved to: {BASE_PATH}/setup_summary.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC ✅ **Deployment setup complete!**
# MAGIC 
# MAGIC This notebook has:
# MAGIC - Created Unity Catalog structure (catalog + 3 schemas)
# MAGIC - Created DBFS directories for data, configs, and checkpoints
# MAGIC - Generated and uploaded configuration files
# MAGIC - Set up MLflow experiment
# MAGIC - Validated the environment
# MAGIC - Provided cluster configuration recommendations
# MAGIC 
# MAGIC **You are now ready to run the demo notebooks!**
# MAGIC 
# MAGIC Execute notebooks in this order:
# MAGIC 1. **01_ingest_synthetic_data** - Generate synthetic transaction data
# MAGIC 2. **02_stream_enrichment_smart_checkout** - Apply Smart Checkout decisions
# MAGIC 3. **03_reason_code_performance** - Analyze decline patterns
# MAGIC 4. **04_smart_retry** - Train ML model for retry optimization
# MAGIC 5. **05_dashboards_and_genie_examples** - Create SQL views
# MAGIC 6. **06_app_demo_ui** - Deploy interactive Command Center
# MAGIC 
# MAGIC **Happy demoing! 🚀**
