# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Synthetic Data Ingestion for Payment Authorization Demo
# MAGIC
# MAGIC ## Overview
# MAGIC This notebook generates synthetic streaming data for card payment transactions with:
# MAGIC - **transactions_raw**: Authorization attempts with payment solution flags
# MAGIC - **cardholders_dim**: Customer dimension with KYC and risk profiles
# MAGIC - **merchants_dim**: Merchant dimension with MCC, geo, and risk data
# MAGIC - **external_risk_signals**: Streaming Moody's-style macro/sector risk scores
# MAGIC
# MAGIC ## Architecture
# MAGIC - Bronze layer: Raw streaming ingestion
# MAGIC - Delta Lake format with time travel
# MAGIC - Structured Streaming in real-time mode

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Imports

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.streaming import StreamingQuery
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Database and catalog configuration
CATALOG = "payments_lakehouse"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

# Create database structure
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_BRONZE}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_SILVER}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_GOLD}")

# Table paths
BRONZE_PATH = f"/dbfs/payments_demo/bronze"
SILVER_PATH = f"/dbfs/payments_demo/silver"
GOLD_PATH = f"/dbfs/payments_demo/gold"
CHECKPOINT_PATH = f"/dbfs/payments_demo/checkpoints"

print(f"✅ Catalog: {CATALOG}")
print(f"✅ Bronze Schema: {SCHEMA_BRONZE}")
print(f"✅ Silver Schema: {SCHEMA_SILVER}")
print(f"✅ Gold Schema: {SCHEMA_GOLD}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dimension Data Generation
# MAGIC
# MAGIC ### Cardholders Dimension

# COMMAND ----------

# Generate synthetic cardholder data
def generate_cardholders(num_cardholders=100000):
    countries = ["US", "UK", "DE", "FR", "ES", "IT", "BR", "MX", "AU", "JP", "IN", "CA", "NL", "SE", "NO"]
    kyc_segments = ["Premium", "Standard", "Basic", "New"]
    
    cardholders_data = []
    for i in range(num_cardholders):
        cardholder_id = f"CH{str(i+1).zfill(8)}"
        country = random.choice(countries)
        kyc_segment = random.choices(
            kyc_segments,
            weights=[10, 50, 30, 10],
            k=1
        )[0]
        
        # Risk score influenced by segment
        base_risk = {"Premium": 0.05, "Standard": 0.15, "Basic": 0.25, "New": 0.35}
        risk_score = min(1.0, max(0.0, base_risk[kyc_segment] + random.gauss(0, 0.1)))
        
        # Customer tenure in months
        tenure_map = {"Premium": (36, 120), "Standard": (12, 60), "Basic": (6, 24), "New": (0, 6)}
        tenure = random.randint(*tenure_map[kyc_segment])
        
        cardholders_data.append({
            "cardholder_id": cardholder_id,
            "country": country,
            "kyc_segment": kyc_segment,
            "risk_score": round(risk_score, 3),
            "customer_tenure_months": tenure,
            "created_date": datetime.now() - timedelta(days=tenure*30)
        })
    
    return spark.createDataFrame(cardholders_data)

# Generate and save cardholders dimension
df_cardholders = generate_cardholders(100000)

# Add Unity Catalog comments
df_cardholders.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_BRONZE}.cardholders_dim")

# Add table and column comments
spark.sql(f"""
COMMENT ON TABLE {CATALOG}.{SCHEMA_BRONZE}.cardholders_dim IS 
'Cardholder dimension table with KYC segment, risk scores, and tenure information'
""")

print(f"✅ Generated {df_cardholders.count():,} cardholders")
display(df_cardholders.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Merchants Dimension

# COMMAND ----------

def generate_merchants(num_merchants=50000):
    """Generate synthetic merchant data with MCC codes and risk profiles"""
    
    # Merchant Category Codes (real MCC codes)
    mcc_categories = {
        5411: {"name": "Grocery Stores", "risk": "low"},
        5812: {"name": "Eating Places", "risk": "low"},
        5999: {"name": "Miscellaneous Retail", "risk": "medium"},
        5967: {"name": "Direct Marketing", "risk": "high"},
        7995: {"name": "Gambling", "risk": "high"},
        5122: {"name": "Drugs and Pharmaceuticals", "risk": "medium"},
        7273: {"name": "Dating Services", "risk": "high"},
        5816: {"name": "Digital Games", "risk": "medium"},
        5732: {"name": "Electronics", "risk": "medium"},
        5735: {"name": "Music Stores", "risk": "low"},
        5945: {"name": "Hobby Shops", "risk": "low"},
        7011: {"name": "Hotels and Motels", "risk": "medium"},
        4511: {"name": "Airlines", "risk": "low"},
        5311: {"name": "Department Stores", "risk": "low"}
    }
    
    countries = ["US", "UK", "DE", "FR", "ES", "IT", "BR", "MX", "AU", "JP", "IN", "CA", "NL", "SE", "NO"]
    acquirers = ["Acquirer_A", "Acquirer_B", "Acquirer_C", "Acquirer_D", "Acquirer_E"]
    merchant_sizes = ["enterprise", "smb", "startup"]
    
    merchants_data = []
    for i in range(num_merchants):
        merchant_id = f"M{str(i+1).zfill(8)}"
        mcc = random.choice(list(mcc_categories.keys()))
        mcc_info = mcc_categories[mcc]
        
        country = random.choice(countries)
        acquirer = random.choice(acquirers)
        merchant_size = random.choices(
            merchant_sizes,
            weights=[20, 60, 20],
            k=1
        )[0]
        
        # Risk score based on MCC and size
        risk_base = {"low": 0.1, "medium": 0.3, "high": 0.6}
        size_modifier = {"enterprise": -0.1, "smb": 0.0, "startup": 0.15}
        
        risk_score = min(1.0, max(0.0, 
            risk_base[mcc_info["risk"]] + 
            size_modifier[merchant_size] + 
            random.gauss(0, 0.1)
        ))
        
        # Determine merchant cluster
        if risk_score < 0.25:
            cluster = "low_risk"
        elif risk_score < 0.5:
            cluster = "medium_risk"
        else:
            cluster = "high_risk"
        
        merchants_data.append({
            "merchant_id": merchant_id,
            "merchant_name": f"{mcc_info['name']} {i+1}",
            "mcc": mcc,
            "mcc_description": mcc_info["name"],
            "country": country,
            "merchant_size": merchant_size,
            "merchant_cluster": cluster,
            "risk_score": round(risk_score, 3),
            "acquirer": acquirer,
            "onboarding_date": datetime.now() - timedelta(days=random.randint(30, 1095))
        })
    
    return spark.createDataFrame(merchants_data)

# Generate and save merchants dimension
df_merchants = generate_merchants(50000)

df_merchants.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_BRONZE}.merchants_dim")

spark.sql(f"""
COMMENT ON TABLE {CATALOG}.{SCHEMA_BRONZE}.merchants_dim IS 
'Merchant dimension with MCC codes, geographic data, risk scores, and acquirer information'
""")

print(f"✅ Generated {df_merchants.count():,} merchants")
display(df_merchants.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ### External Risk Signals - Moody's-style Data

# COMMAND ----------

def generate_external_risk_signals():
    """Generate synthetic Moody's-style macroeconomic and sector risk data"""
    
    countries = ["US", "UK", "DE", "FR", "ES", "IT", "BR", "MX", "AU", "JP", "IN", "CA", "NL", "SE", "NO"]
    sectors = ["Retail", "Hospitality", "Technology", "Healthcare", "Finance", "Gambling", "Crypto"]
    
    risk_data = []
    
    for country in countries:
        # Country-level macro risk (0-1 scale)
        base_country_risk = {
            "US": 0.15, "UK": 0.18, "DE": 0.12, "FR": 0.20, "ES": 0.30,
            "IT": 0.35, "BR": 0.50, "MX": 0.45, "AU": 0.10, "JP": 0.15,
            "IN": 0.40, "CA": 0.12, "NL": 0.10, "SE": 0.08, "NO": 0.08
        }
        
        country_risk = base_country_risk.get(country, 0.25)
        
        for sector in sectors:
            # Sector risk varies by sector type
            sector_base_risk = {
                "Retail": 0.25, "Hospitality": 0.30, "Technology": 0.15,
                "Healthcare": 0.10, "Finance": 0.20, "Gambling": 0.60,
                "Crypto": 0.75
            }
            
            sector_risk = sector_base_risk.get(sector, 0.25)
            
            # Combined risk with some randomness
            combined_risk = min(1.0, (country_risk + sector_risk) / 2 + random.gauss(0, 0.05))
            
            risk_data.append({
                "country": country,
                "sector": sector,
                "country_risk_score": round(country_risk, 3),
                "sector_risk_score": round(sector_risk, 3),
                "combined_risk_score": round(combined_risk, 3),
                "gdp_growth_rate": round(random.gauss(2.5, 1.5), 2),
                "unemployment_rate": round(random.gauss(6.0, 2.0), 2),
                "inflation_rate": round(random.gauss(3.0, 1.5), 2),
                "sanctions_flag": random.choice([0, 0, 0, 0, 1]) if country in ["BR", "MX", "IN"] else 0,
                "aml_risk_level": random.choice(["Low", "Medium", "High", "Critical"]),
                "timestamp": datetime.now()
            })
    
    return spark.createDataFrame(risk_data)

# Generate external risk signals
df_risk_signals = generate_external_risk_signals()

df_risk_signals.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_BRONZE}.external_risk_signals")

spark.sql(f"""
COMMENT ON TABLE {CATALOG}.{SCHEMA_BRONZE}.external_risk_signals IS 
'External risk signals including Moody''s-style macro indicators, sector risks, and AML data'
""")

print(f"✅ Generated {df_risk_signals.count():,} risk signal records")
display(df_risk_signals)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Streaming Transaction Data Generation
# MAGIC
# MAGIC This simulates a Kafka/Event Hubs source with real-time transaction authorization attempts.

# COMMAND ----------

# DBTITLE 1,Cell 13
def generate_transaction_stream_batch(batch_id, num_transactions=1000):
    """Generate a batch of synthetic transaction authorization attempts"""
    
    # Load dimension tables for realistic joins
    cardholders = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.cardholders_dim").collect()
    merchants = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.merchants_dim").collect()
    
    channels = ["ecommerce", "mpos", "pos", "recurring", "moto"]
    card_networks = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]
    currencies = ["USD", "EUR", "GBP", "BRL", "MXN", "AUD", "JPY", "INR", "CAD"]
    
    # Payment solution flags
    payment_solutions = ["3DS", "Antifraud", "IDPay", "DataShareOnly", "NetworkToken", "Passkey"]
    
    # Reason codes
    reason_codes = [
        "00_APPROVED", "05_DO_NOT_HONOR", "14_INVALID_CARD", "51_INSUFFICIENT_FUNDS",
        "54_EXPIRED_CARD", "57_FUNCTION_NOT_PERMITTED", "61_EXCEEDS_LIMIT",
        "62_RESTRICTED_CARD", "63_SECURITY_VIOLATION", "65_EXCEEDS_FREQUENCY",
        "91_ISSUER_UNAVAILABLE", "96_SYSTEM_ERROR"
    ]
    
    transactions = []
    
    for i in range(num_transactions):
        cardholder = random.choice(cardholders)
        merchant = random.choice(merchants)
        
        transaction_id = f"TXN{batch_id}_{str(i+1).zfill(6)}"
        timestamp = datetime.now()
        
        # Channel selection
        channel = random.choices(
            channels,
            weights=[50, 20, 15, 10, 5],
            k=1
        )[0]
        
        # Amount generation (log-normal distribution)
        amount = round(random.lognormvariate(4.0, 1.5), 2)
        
        # Currency based on cardholder country
        currency_map = {
            "US": "USD", "UK": "GBP", "DE": "EUR", "FR": "EUR", "ES": "EUR",
            "IT": "EUR", "BR": "BRL", "MX": "MXN", "AU": "AUD", "JP": "JPY",
            "IN": "INR", "CA": "CAD", "NL": "EUR", "SE": "EUR", "NO": "EUR"
        }
        currency = currency_map.get(cardholder.country, "USD")
        
        # Card network
        card_network = random.choices(
            card_networks,
            weights=[45, 35, 15, 5],
            k=1
        )[0]
        
        # Payment solution flags (randomly selected combination)
        active_solutions = random.sample(payment_solutions, k=random.randint(0, 3))
        solution_flags = {sol: (sol in active_solutions) for sol in payment_solutions}
        
        # Calculate combined risk score
        combined_risk = (
            cardholder.risk_score * 0.4 +
            merchant.risk_score * 0.4 +
            (0.2 if channel == "ecommerce" else 0.0) +
            random.gauss(0, 0.1)
        )
        combined_risk = min(1.0, max(0.0, combined_risk))
        
        # Determine approval based on risk and solutions
        # More solutions = higher approval probability
        base_approval_prob = 0.85
        risk_penalty = combined_risk * 0.3
        solution_bonus = len(active_solutions) * 0.03
        
        approval_prob = base_approval_prob - risk_penalty + solution_bonus
        is_approved = random.random() < approval_prob
        
        # Reason code
        if is_approved:
            reason_code = "00_APPROVED"
        else:
            # Weight decline codes realistically
            reason_code = random.choices(
                [rc for rc in reason_codes if rc != "00_APPROVED"],
                weights=[25, 5, 15, 5, 10, 10, 8, 12, 5, 5, 5],
                k=1
            )[0]
        
        # Is this a retry?
        is_retry = random.random() < 0.15  # 15% are retries
        retry_attempt_number = random.randint(1, 5) if is_retry else 0
        
        # Is recurring payment?
        is_recurring = channel == "recurring"
        
        transactions.append({
            "transaction_id": transaction_id,
            "timestamp": timestamp,
            "cardholder_id": cardholder.cardholder_id,
            "merchant_id": merchant.merchant_id,
            "amount": amount,
            "currency": currency,
            "channel": channel,
            "card_network": card_network,
            "mcc": merchant.mcc,
            "cardholder_country": cardholder.country,
            "merchant_country": merchant.country,
            "is_cross_border": cardholder.country != merchant.country,
            "flag_3DS": solution_flags["3DS"],
            "flag_Antifraud": solution_flags["Antifraud"],
            "flag_IDPay": solution_flags["IDPay"],
            "flag_DataShareOnly": solution_flags["DataShareOnly"],
            "flag_NetworkToken": solution_flags["NetworkToken"],
            "flag_Passkey": solution_flags["Passkey"],
            "combined_risk_score": round(combined_risk, 3),
            "is_approved": is_approved,
            "reason_code": reason_code,
            "is_retry": is_retry,
            "retry_attempt_number": retry_attempt_number,
            "is_recurring": is_recurring,
            "processing_time_ms": random.randint(50, 500)
        })
    
    return spark.createDataFrame(transactions)

# Test generation
df_test_batch = generate_transaction_stream_batch(batch_id=0, num_transactions=100)
print(f"✅ Generated test batch of {df_test_batch.count()} transactions")
display(df_test_batch)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Streaming Source
# MAGIC
# MAGIC We'll use rate source to trigger periodic batch generation, simulating a Kafka stream.

# COMMAND ----------

# Create streaming rate source (triggers every 10 seconds)
rate_stream = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 100) \
    .load()

print("✅ Rate stream created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Streaming Transactions to Bronze Layer

# COMMAND ----------

# Counter for batch IDs
from pyspark.sql.functions import col, expr

def process_transaction_batch(batch_df, batch_id):
    """Process each micro-batch and generate synthetic transactions"""
    
    if batch_df.isEmpty():
        return
    
    # Generate transactions for this batch
    num_transactions = 1000  # Generate 1000 transactions per batch
    transactions_df = generate_transaction_stream_batch(batch_id, num_transactions)
    
    # Write to Delta Bronze table
    transactions_df.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable(f"{CATALOG}.{SCHEMA_BRONZE}.transactions_raw")
    
    print(f"✅ Batch {batch_id}: Wrote {num_transactions} transactions to Bronze")

# Start streaming query
streaming_query = rate_stream.writeStream \
    .foreachBatch(process_transaction_batch) \
    .option("checkpointLocation", f"{CHECKPOINT_PATH}/transactions_raw") \
    .trigger(availableNow=True) \
    .start()

print("✅ Streaming ingestion started")
print(f"   Query ID: {streaming_query.id}")
print(f"   Status: {streaming_query.status}")
print("\n⚠️  Streaming query is running. It will generate transactions every 10 seconds.")
print("   Run the next cell to stop the stream after collecting some data.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Monitor Streaming Ingestion

# COMMAND ----------

# Let it run for a bit to generate data (adjust the sleep time as needed)
import time

print("⏳ Collecting streaming data for 60 seconds...")
time.sleep(60)

# Check current status
print(f"\n📊 Stream Status: {streaming_query.status}")
print(f"   Is Active: {streaming_query.isActive}")
print(f"   Recent Progress:")

# Show recent progress
try:
    recent_progress = streaming_query.recentProgress
    if recent_progress:
        latest = recent_progress[-1]
        print(f"   - Batch: {latest.get('batchId', 'N/A')}")
        print(f"   - Num Input Rows: {latest.get('numInputRows', 'N/A')}")
        print(f"   - Input Rows/Sec: {latest.get('inputRowsPerSecond', 'N/A')}")
        print(f"   - Process Rows/Sec: {latest.get('processedRowsPerSecond', 'N/A')}")
except Exception as e:
    print(f"   Could not fetch progress: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stop Streaming Query

# COMMAND ----------

# Stop the streaming query
streaming_query.stop()
print("✅ Streaming query stopped")

# Wait for graceful shutdown
time.sleep(5)

# Verify data was written
transaction_count = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.transactions_raw").count()
print(f"\n📊 Total transactions in Bronze layer: {transaction_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Bronze Layer Data

# COMMAND ----------

# Load and display Bronze tables
print("=" * 80)
print("BRONZE LAYER SUMMARY")
print("=" * 80)

# Cardholders
cardholders_count = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.cardholders_dim").count()
print(f"✅ Cardholders: {cardholders_count:,}")

# Merchants
merchants_count = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.merchants_dim").count()
print(f"✅ Merchants: {merchants_count:,}")

# External Risk Signals
risk_signals_count = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.external_risk_signals").count()
print(f"✅ External Risk Signals: {risk_signals_count:,}")

# Transactions
transactions_count = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.transactions_raw").count()
print(f"✅ Transactions: {transactions_count:,}")

print("=" * 80)

# Display sample transactions with all details
df_sample_transactions = spark.table(f"{CATALOG}.{SCHEMA_BRONZE}.transactions_raw").limit(20)
display(df_sample_transactions)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analytics: Initial Approval Rate Baseline

# COMMAND ----------

# Calculate baseline approval rates
df_baseline = spark.sql(f"""
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN is_approved THEN 1 ELSE 0 END) as approved_count,
    ROUND(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(combined_risk_score), 3) as avg_risk_score,
    COUNT(DISTINCT cardholder_id) as unique_cardholders,
    COUNT(DISTINCT merchant_id) as unique_merchants
FROM {CATALOG}.{SCHEMA_BRONZE}.transactions_raw
""")

display(df_baseline)

# Approval rates by channel
df_by_channel = spark.sql(f"""
SELECT 
    channel,
    COUNT(*) as total_transactions,
    ROUND(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(amount), 2) as avg_amount
FROM {CATALOG}.{SCHEMA_BRONZE}.transactions_raw
GROUP BY channel
ORDER BY approval_rate_pct DESC
""")

display(df_by_channel)

# Decline reasons distribution
df_decline_reasons = spark.sql(f"""
SELECT 
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_declines
FROM {CATALOG}.{SCHEMA_BRONZE}.transactions_raw
WHERE NOT is_approved
GROUP BY reason_code
ORDER BY decline_count DESC
""")

display(df_decline_reasons)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Bronze Layer Complete**:
# MAGIC - Cardholder dimension with 100K customers
# MAGIC - Merchant dimension with 50K merchants
# MAGIC - External risk signals (Moody's-style)
# MAGIC - Streaming transaction data with authorization attempts
# MAGIC
# MAGIC **Key Features**:
# MAGIC - Payment solution flags (3DS, Antifraud, IDPay, DataShareOnly, NetworkToken, Passkey)
# MAGIC - Realistic decline reason codes
# MAGIC - Risk scoring at cardholder, merchant, and transaction level
# MAGIC - Cross-border transaction detection
# MAGIC - Retry and recurring payment flags
# MAGIC
# MAGIC **Next Steps**:
# MAGIC - Notebook 02: Stream enrichment and Smart Checkout decisioning
# MAGIC - Notebook 03: Reason Code Performance analytics
# MAGIC - Notebook 04: Smart Retry module
