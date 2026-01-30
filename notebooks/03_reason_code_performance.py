# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Reason Code Performance Analytics
# MAGIC 
# MAGIC ## Overview
# MAGIC This notebook implements near real-time analytics on decline reason codes to generate actionable insights:
# MAGIC - **Reason Code Taxonomy**: Standardized mapping and categorization
# MAGIC - **Real-time Aggregations**: By issuer, merchant, BIN, geography, channel, solution mix
# MAGIC - **Root Cause Analysis**: Identify patterns and actionable remediation steps
# MAGIC - **Feedback Loop**: Insights feed back into Smart Checkout configuration
# MAGIC 
# MAGIC ## Business Goal
# MAGIC Convert decline analytics into actionable recommendations to reduce future declines.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Imports

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime, timedelta
import json

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

CATALOG = "payments_lakehouse"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

spark.sql(f"USE CATALOG {CATALOG}")

# Load reason code taxonomy
with open("/dbfs/payments_demo/config/reason_codes.json", "r") as f:
    REASON_CODE_CONFIG = json.load(f)

reason_code_taxonomy = REASON_CODE_CONFIG["reason_code_taxonomy"]

print("✅ Configuration loaded")
print(f"   Reason Codes in Taxonomy: {len(reason_code_taxonomy)}")
print(f"   Categories: {set(rc['category'] for rc in reason_code_taxonomy.values())}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Reason Code Dimension Table

# COMMAND ----------

def create_reason_code_dimension():
    """Create a dimension table for reason codes with full taxonomy"""
    
    reason_code_data = []
    
    for code, details in reason_code_taxonomy.items():
        reason_code_data.append({
            "reason_code": code,
            "category": details["category"],
            "severity": details["severity"],
            "is_actionable": details["actionable"],
            "description": details["description"],
            "root_causes": details.get("root_causes", []),
            "recommended_actions": details.get("recommended_actions", [])
        })
    
    df_reason_codes = spark.createDataFrame(reason_code_data)
    
    # Write to Bronze as a dimension
    df_reason_codes.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SCHEMA_BRONZE}.reason_code_dim")
    
    spark.sql(f"""
    COMMENT ON TABLE {CATALOG}.{SCHEMA_BRONZE}.reason_code_dim IS 
    'Reason code dimension with standardized taxonomy, categories, and recommended actions'
    """)
    
    print("✅ Reason code dimension created")
    return df_reason_codes

df_reason_codes = create_reason_code_dimension()
display(df_reason_codes)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Real-Time Decline Aggregations

# COMMAND ----------

# Read enriched stream from Silver
df_enriched = spark.table(f"{CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream")

# Filter for declines only
df_declines = df_enriched.filter(F.col("is_approved") == False)

print(f"✅ Loaded enriched stream for decline analysis")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 1: Decline Rate by Reason Code

# COMMAND ----------

# Overall decline distribution
df_decline_distribution = spark.sql(f"""
SELECT 
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_declines,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score,
    ROUND(AVG(amount), 2) as avg_amount
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY reason_code
ORDER BY decline_count DESC
""")

print("\n📊 Decline Distribution by Reason Code:")
display(df_decline_distribution)

# Save to Gold
df_decline_distribution.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_distribution")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 2: Decline Rate by Issuer

# COMMAND ----------

df_decline_by_issuer = spark.sql(f"""
SELECT 
    card_network as issuer,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY card_network), 2) as pct_of_issuer_declines,
    ROUND(AVG(amount), 2) as avg_amount,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY card_network, reason_code
ORDER BY card_network, decline_count DESC
""")

print("\n📊 Decline Distribution by Issuer and Reason Code:")
display(df_decline_by_issuer.limit(50))

# Save to Gold
df_decline_by_issuer.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_by_issuer")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 3: Decline Rate by Geography

# COMMAND ----------

df_decline_by_geography = spark.sql(f"""
SELECT 
    cardholder_country as geography,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY cardholder_country), 2) as pct_of_geo_declines,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY cardholder_country, reason_code
ORDER BY cardholder_country, decline_count DESC
""")

print("\n🌍 Decline Distribution by Geography:")
display(df_decline_by_geography.limit(50))

# Save to Gold
df_decline_by_geography.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_by_geography")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 4: Decline Rate by Merchant Segment

# COMMAND ----------

df_decline_by_merchant = spark.sql(f"""
SELECT 
    merchant_cluster,
    mcc,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY merchant_cluster), 2) as pct_of_cluster_declines,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY merchant_cluster, mcc, reason_code
ORDER BY merchant_cluster, decline_count DESC
""")

print("\n🏪 Decline Distribution by Merchant Cluster:")
display(df_decline_by_merchant.limit(50))

# Save to Gold
df_decline_by_merchant.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_by_merchant_cluster")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 5: Decline Rate by Payment Solution Mix

# COMMAND ----------

df_decline_by_solution = spark.sql(f"""
SELECT 
    recommended_solution_name,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY recommended_solution_name), 2) as pct_of_solution_declines,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY recommended_solution_name, reason_code
ORDER BY recommended_solution_name, decline_count DESC
""")

print("\n💳 Decline Distribution by Payment Solution Mix:")
display(df_decline_by_solution.limit(50))

# Save to Gold
df_decline_by_solution.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_by_solution_mix")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation 6: Decline Rate by Channel

# COMMAND ----------

df_decline_by_channel = spark.sql(f"""
SELECT 
    channel,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY channel), 2) as pct_of_channel_declines,
    ROUND(AVG(amount), 2) as avg_amount
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY channel, reason_code
ORDER BY channel, decline_count DESC
""")

print("\n📱 Decline Distribution by Channel:")
display(df_decline_by_channel)

# Save to Gold
df_decline_by_channel.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_by_channel")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Time Series: Decline Trends

# COMMAND ----------

df_decline_trends = spark.sql(f"""
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    reason_code,
    COUNT(*) as decline_count,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY DATE_TRUNC('hour', timestamp), reason_code
ORDER BY hour DESC, decline_count DESC
""")

print("\n📈 Decline Trends Over Time (Hourly):")
display(df_decline_trends.limit(100))

# Save to Gold
df_decline_trends.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_trends")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Root Cause Analysis & Actionable Insights
# MAGIC 
# MAGIC Generate specific, actionable insights by identifying decline patterns.

# COMMAND ----------

def generate_actionable_insights():
    """
    Analyze decline patterns and generate specific actionable recommendations.
    """
    
    insights = []
    
    # Insight 1: High-impact reason codes
    high_impact_declines = spark.sql(f"""
    SELECT 
        reason_code,
        COUNT(*) as decline_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream WHERE NOT is_approved), 2) as pct_total
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved
    GROUP BY reason_code
    HAVING COUNT(*) > 100
    ORDER BY decline_count DESC
    LIMIT 5
    """).collect()
    
    for row in high_impact_declines:
        reason_code = row["reason_code"]
        decline_count = row["decline_count"]
        pct_total = row["pct_total"]
        
        # Get recommended actions from taxonomy
        actions = reason_code_taxonomy.get(reason_code, {}).get("recommended_actions", [])
        root_causes = reason_code_taxonomy.get(reason_code, {}).get("root_causes", [])
        
        insights.append({
            "insight_id": f"HIGH_IMPACT_{reason_code}",
            "segment": "Overall",
            "issue": f"High volume of {reason_code} declines ({decline_count:,} transactions, {pct_total}% of all declines)",
            "root_causes": root_causes,
            "recommended_actions": actions,
            "priority": "High",
            "estimated_impact": f"Addressing this could recover {pct_total}% of declined transactions"
        })
    
    # Insight 2: Issuer-specific patterns
    issuer_anomalies = spark.sql(f"""
    SELECT 
        card_network as issuer,
        reason_code,
        COUNT(*) as decline_count,
        ROUND(AVG(composite_risk_score), 3) as avg_risk_score
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved
    GROUP BY card_network, reason_code
    HAVING COUNT(*) > 50
    ORDER BY decline_count DESC
    LIMIT 10
    """).collect()
    
    for row in issuer_anomalies:
        issuer = row["issuer"]
        reason_code = row["reason_code"]
        decline_count = row["decline_count"]
        avg_risk = row["avg_risk_score"]
        
        actions = reason_code_taxonomy.get(reason_code, {}).get("recommended_actions", [])
        
        insights.append({
            "insight_id": f"ISSUER_{issuer}_{reason_code}",
            "segment": f"Issuer: {issuer}",
            "issue": f"{issuer} shows elevated {reason_code} declines ({decline_count:,} transactions, avg risk: {avg_risk})",
            "root_causes": [f"Issuer-specific rules or risk thresholds for {issuer}"],
            "recommended_actions": [
                f"Contact {issuer} to understand decline triggers",
                f"Consider alternative routing for {issuer} transactions"
            ] + actions,
            "priority": "Medium",
            "estimated_impact": f"Could improve {issuer} approval rate by 3-8%"
        })
    
    # Insight 3: Geography-specific issues
    geo_issues = spark.sql(f"""
    SELECT 
        cardholder_country as geography,
        reason_code,
        COUNT(*) as decline_count,
        ROUND(AVG(country_risk_score), 3) as avg_country_risk
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved AND cardholder_country IS NOT NULL
    GROUP BY cardholder_country, reason_code
    HAVING COUNT(*) > 50
    ORDER BY decline_count DESC
    LIMIT 10
    """).collect()
    
    for row in geo_issues:
        geography = row["geography"]
        reason_code = row["reason_code"]
        decline_count = row["decline_count"]
        
        insights.append({
            "insight_id": f"GEO_{geography}_{reason_code}",
            "segment": f"Geography: {geography}",
            "issue": f"{geography} transactions have elevated {reason_code} declines ({decline_count:,})",
            "root_causes": [
                f"Geographic restrictions for {geography}",
                "Cross-border transaction controls",
                "Local regulatory requirements"
            ],
            "recommended_actions": [
                f"Enable 3DS for all {geography} transactions",
                f"Use local acquirers in {geography}",
                "Implement geo-specific routing rules"
            ],
            "priority": "Medium",
            "estimated_impact": f"Could improve {geography} approval rate by 5-12%"
        })
    
    # Insight 4: Merchant cluster issues
    merchant_issues = spark.sql(f"""
    SELECT 
        merchant_cluster,
        reason_code,
        COUNT(*) as decline_count,
        ROUND(AVG(merchant_risk_score), 3) as avg_merchant_risk
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved
    GROUP BY merchant_cluster, reason_code
    HAVING COUNT(*) > 30
    ORDER BY decline_count DESC
    LIMIT 10
    """).collect()
    
    for row in merchant_issues:
        cluster = row["merchant_cluster"]
        reason_code = row["reason_code"]
        decline_count = row["decline_count"]
        
        insights.append({
            "insight_id": f"MERCHANT_{cluster}_{reason_code}",
            "segment": f"Merchant Cluster: {cluster}",
            "issue": f"{cluster} merchants see elevated {reason_code} declines ({decline_count:,})",
            "root_causes": [
                f"Risk profile of {cluster} merchants",
                "MCC-specific issuer restrictions",
                "Historical fraud patterns"
            ],
            "recommended_actions": [
                f"Require enhanced security for {cluster} merchants",
                "Implement tiered authentication based on amount",
                "Use Antifraud + 3DS combination"
            ],
            "priority": "High" if cluster == "high_risk" else "Medium",
            "estimated_impact": f"Could reduce {cluster} decline rate by 8-15%"
        })
    
    # Insight 5: Solution mix optimization
    solution_inefficiencies = spark.sql(f"""
    SELECT 
        recommended_solution_name,
        reason_code,
        COUNT(*) as decline_count,
        ROUND(AVG(solution_cost), 2) as avg_cost
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved
    GROUP BY recommended_solution_name, reason_code
    HAVING COUNT(*) > 30
    ORDER BY decline_count DESC
    LIMIT 10
    """).collect()
    
    for row in solution_inefficiencies:
        solution = row["recommended_solution_name"]
        reason_code = row["reason_code"]
        decline_count = row["decline_count"]
        
        insights.append({
            "insight_id": f"SOLUTION_{solution}_{reason_code}",
            "segment": f"Solution Mix: {solution}",
            "issue": f"{solution} combination still results in {reason_code} declines ({decline_count:,})",
            "root_causes": [
                "Insufficient security for this transaction profile",
                "Issuer not recognizing solution benefits",
                "Integration or messaging issues"
            ],
            "recommended_actions": [
                f"Enhance {solution} with additional authentication",
                "Verify solution is properly implemented",
                "Consider alternative solution combinations"
            ],
            "priority": "Medium",
            "estimated_impact": "Could improve solution effectiveness by 10-20%"
        })
    
    return insights

# Generate insights
insights = generate_actionable_insights()

print(f"\n✅ Generated {len(insights)} actionable insights")

# Convert to DataFrame
df_insights = spark.createDataFrame(insights)

# Save to Gold
df_insights.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.reason_code_insights")

spark.sql(f"""
COMMENT ON TABLE {CATALOG}.{SCHEMA_GOLD}.reason_code_insights IS 
'Actionable insights derived from decline reason code analysis with root causes and recommendations'
""")

display(df_insights)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feedback Loop: Update Smart Checkout Configuration

# COMMAND ----------

def generate_smart_checkout_config_updates():
    """
    Generate recommended configuration updates for Smart Checkout based on decline insights.
    """
    
    config_updates = []
    
    # Find combinations with high decline rates for specific reason codes
    problematic_combos = spark.sql(f"""
    SELECT 
        recommended_solution_name,
        card_network,
        cardholder_country,
        reason_code,
        COUNT(*) as decline_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY recommended_solution_name, card_network, cardholder_country), 2) as decline_rate_pct
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    WHERE NOT is_approved
    GROUP BY recommended_solution_name, card_network, cardholder_country, reason_code
    HAVING decline_rate_pct > 30
    ORDER BY decline_count DESC
    LIMIT 20
    """).collect()
    
    for row in problematic_combos:
        solution = row["recommended_solution_name"]
        issuer = row["card_network"]
        country = row["cardholder_country"]
        reason_code = row["reason_code"]
        decline_rate = row["decline_rate_pct"]
        
        # Recommend specific changes
        if reason_code == "63_SECURITY_VIOLATION":
            new_solution = "3DS+Antifraud+IDPay"
            rationale = "Security violation requires enhanced authentication"
        elif reason_code == "05_DO_NOT_HONOR":
            new_solution = "NetworkToken+3DS"
            rationale = "Generic decline may be resolved with network tokenization"
        elif reason_code == "61_EXCEEDS_LIMIT":
            new_solution = "DataShareOnly"
            rationale = "Lighter solution may help with limit issues"
        else:
            new_solution = solution + "+Antifraud"
            rationale = "Add fraud screening for elevated decline rate"
        
        config_updates.append({
            "update_id": f"CONFIG_{solution}_{issuer}_{country}_{reason_code}",
            "segment": f"{issuer} in {country}",
            "current_solution": solution,
            "recommended_solution": new_solution,
            "reason_code_trigger": reason_code,
            "current_decline_rate_pct": decline_rate,
            "rationale": rationale,
            "priority": "High" if decline_rate > 50 else "Medium"
        })
    
    return config_updates

# Generate configuration updates
config_updates = generate_smart_checkout_config_updates()

print(f"\n✅ Generated {len(config_updates)} Smart Checkout configuration recommendations")

# Convert to DataFrame
df_config_updates = spark.createDataFrame(config_updates)

# Save to Gold
df_config_updates.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.smart_checkout_config_recommendations")

display(df_config_updates)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Heatmap Data: Issuer vs Reason Code

# COMMAND ----------

# Create pivot table for heatmap visualization
df_heatmap = spark.sql(f"""
SELECT 
    card_network as issuer,
    reason_code,
    COUNT(*) as decline_count
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
GROUP BY card_network, reason_code
ORDER BY card_network, reason_code
""")

# Pivot for heatmap
df_heatmap_pivot = df_heatmap.groupBy("issuer").pivot("reason_code").sum("decline_count").fillna(0)

print("\n🔥 Heatmap: Issuer vs Reason Code")
display(df_heatmap_pivot)

# Save to Gold
df_heatmap_pivot.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.decline_heatmap_issuer_reason")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

# Overall decline summary
df_decline_summary = spark.sql(f"""
SELECT 
    COUNT(*) as total_declines,
    COUNT(DISTINCT cardholder_id) as unique_cardholders_declined,
    COUNT(DISTINCT merchant_id) as unique_merchants_declined,
    COUNT(DISTINCT reason_code) as unique_reason_codes,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score_declined,
    ROUND(AVG(amount), 2) as avg_amount_declined,
    SUM(CASE WHEN reason_code IN ('05_DO_NOT_HONOR', '51_INSUFFICIENT_FUNDS', '61_EXCEEDS_LIMIT', '65_EXCEEDS_FREQUENCY', '91_ISSUER_UNAVAILABLE') THEN 1 ELSE 0 END) as soft_declines,
    SUM(CASE WHEN reason_code IN ('14_INVALID_CARD', '54_EXPIRED_CARD', '62_RESTRICTED_CARD') THEN 1 ELSE 0 END) as hard_declines,
    SUM(CASE WHEN reason_code IN ('63_SECURITY_VIOLATION') THEN 1 ELSE 0 END) as security_declines,
    SUM(CASE WHEN reason_code IN ('91_ISSUER_UNAVAILABLE', '96_SYSTEM_ERROR') THEN 1 ELSE 0 END) as technical_declines
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
WHERE NOT is_approved
""")

print("\n📊 Decline Summary:")
display(df_decline_summary)

# Category breakdown
df_category_breakdown = spark.sql(f"""
SELECT 
    rc.category,
    COUNT(txn.transaction_id) as decline_count,
    ROUND(COUNT(txn.transaction_id) * 100.0 / (SELECT COUNT(*) FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream WHERE NOT is_approved), 2) as pct_of_declines,
    ROUND(AVG(txn.composite_risk_score), 3) as avg_risk_score
FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream txn
JOIN {CATALOG}.{SCHEMA_BRONZE}.reason_code_dim rc ON txn.reason_code = rc.reason_code
WHERE NOT txn.is_approved
GROUP BY rc.category
ORDER BY decline_count DESC
""")

print("\n📊 Decline Category Breakdown:")
display(df_category_breakdown)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC ✅ **Reason Code Performance Module Complete**:
# MAGIC - Standardized reason code taxonomy with 12 mapped codes
# MAGIC - Real-time aggregations by issuer, geography, merchant, channel, and solution mix
# MAGIC - Time-series decline trends for monitoring
# MAGIC - Heatmap data for issuer vs reason code visualization
# MAGIC 
# MAGIC ✅ **Actionable Insights Generated**:
# MAGIC - High-impact decline patterns identified
# MAGIC - Root cause analysis by segment
# MAGIC - Specific remediation recommendations
# MAGIC - Smart Checkout configuration update suggestions
# MAGIC 
# MAGIC **Key Findings**:
# MAGIC - Soft declines (05, 51, 61, 65, 91) represent the largest opportunity for recovery
# MAGIC - Security violations (63) require enhanced authentication stacks
# MAGIC - Geographic and issuer-specific patterns drive different decline behaviors
# MAGIC - Solution mix effectiveness varies by segment
# MAGIC 
# MAGIC **Feedback Loop**:
# MAGIC - Insights feed directly into Smart Checkout policy updates
# MAGIC - Configuration recommendations prioritized by impact
# MAGIC - Continuous monitoring enables dynamic optimization
# MAGIC 
# MAGIC **Next Steps**:
# MAGIC - Notebook 04: Smart Retry module with ML-based retry timing optimization
# MAGIC - Notebook 05: Dashboards and Genie examples for business users
