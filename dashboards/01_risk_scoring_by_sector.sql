-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Dashboard 1: Risk Scoring Analysis by Sector & Industry
-- MAGIC
-- MAGIC **Purpose:** Monitor risk scores across different merchant sectors and industries to identify high-risk segments and optimize routing strategies.
-- MAGIC
-- MAGIC **Key Metrics:**
-- MAGIC - Risk score distribution by sector
-- MAGIC - Fraud rate by industry
-- MAGIC - High-risk transaction concentration
-- MAGIC - Risk trend analysis
-- MAGIC - Sector-specific decline patterns

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 1: Risk Score Overview by Sector

-- COMMAND ----------

-- DBTITLE 1,Cell 3
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_risk_by_sector AS
SELECT 
  m.merchant_cluster,
  m.mcc_description,
  COUNT(DISTINCT t.transaction_id) AS total_transactions,
  AVG(t.composite_risk_score) AS avg_risk_score,
  PERCENTILE(t.composite_risk_score, 0.50) AS median_risk_score,
  PERCENTILE(t.composite_risk_score, 0.90) AS p90_risk_score,
  PERCENTILE(t.composite_risk_score, 0.95) AS p95_risk_score,
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN 1 ELSE 0 END) AS high_risk_count,
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS high_risk_percentage,
  AVG(t.amount) AS avg_transaction_amount,
  SUM(t.amount) AS total_volume,
  SUM(CASE WHEN NOT t.is_approved AND t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) AS fraud_declines,
  SUM(CASE WHEN NOT t.is_approved AND t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS fraud_rate
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY m.merchant_cluster, m.mcc_description
ORDER BY avg_risk_score DESC;

-- Visualization Type: Bar Chart
-- X-axis: merchant_cluster
-- Y-axis: avg_risk_score
-- Color: high_risk_percentage
-- Tooltip: total_transactions, fraud_rate, total_volume

SELECT * FROM payments_lakehouse.gold.dashboard_risk_by_sector;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 2: Risk Score Distribution Histogram

-- COMMAND ----------

-- DBTITLE 1,Cell 5
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_risk_distribution AS
SELECT 
  CASE 
    WHEN t.composite_risk_score BETWEEN 0.0 AND 0.1 THEN '0.0-0.1 (Very Low)'
    WHEN t.composite_risk_score BETWEEN 0.1 AND 0.2 THEN '0.1-0.2 (Low)'
    WHEN t.composite_risk_score BETWEEN 0.2 AND 0.3 THEN '0.2-0.3 (Low-Med)'
    WHEN t.composite_risk_score BETWEEN 0.3 AND 0.4 THEN '0.3-0.4 (Medium)'
    WHEN t.composite_risk_score BETWEEN 0.4 AND 0.5 THEN '0.4-0.5 (Medium)'
    WHEN t.composite_risk_score BETWEEN 0.5 AND 0.6 THEN '0.5-0.6 (Med-High)'
    WHEN t.composite_risk_score BETWEEN 0.6 AND 0.7 THEN '0.6-0.7 (High)'
    WHEN t.composite_risk_score BETWEEN 0.7 AND 0.8 THEN '0.7-0.8 (High)'
    WHEN t.composite_risk_score BETWEEN 0.8 AND 0.9 THEN '0.8-0.9 (Very High)'
    WHEN t.composite_risk_score BETWEEN 0.9 AND 1.0 THEN '0.9-1.0 (Critical)'
  END AS risk_bucket,
  m.merchant_cluster,
  COUNT(*) AS transaction_count,
  AVG(t.amount) AS avg_amount,
  SUM(t.amount) AS total_amount,
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) AS decline_count,
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS decline_rate
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY risk_bucket, m.merchant_cluster
ORDER BY risk_bucket, m.merchant_cluster;

-- Visualization Type: Stacked Bar Chart
-- X-axis: risk_bucket
-- Y-axis: transaction_count
-- Stack by: merchant_cluster
-- Color scale: Red gradient (higher = more critical)

SELECT * FROM payments_lakehouse.gold.dashboard_risk_distribution;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 3: Sector Risk Heatmap (Hourly)

-- COMMAND ----------

-- DBTITLE 1,Cell 7
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_sector_risk_hourly AS
SELECT 
  DATE_TRUNC('hour', t.timestamp) AS hour,
  m.merchant_cluster,
  AVG(t.composite_risk_score) AS avg_risk_score,
  COUNT(*) AS transaction_count,
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN 1 ELSE 0 END) AS high_risk_txns,
  AVG(t.country_risk_score) AS avg_country_risk,
  AVG(t.sector_risk_score) AS avg_sector_risk
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 24 HOURS
GROUP BY hour, m.merchant_cluster
ORDER BY hour DESC, m.merchant_cluster;

-- Visualization Type: Heatmap
-- X-axis: hour
-- Y-axis: merchant_cluster
-- Color intensity: avg_risk_score
-- Color scale: White -> Yellow -> Red

SELECT * FROM payments_lakehouse.gold.dashboard_sector_risk_hourly;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 4: High-Risk Industry Spotlight

-- COMMAND ----------

-- DBTITLE 1,Cell 9
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_high_risk_industries AS
SELECT 
  m.mcc_description AS merchant_sector,
  m.merchant_cluster AS merchant_category,
  m.mcc AS mcc_code,
  COUNT(DISTINCT t.transaction_id) AS total_transactions,
  COUNT(DISTINCT t.merchant_id) AS merchant_count,
  AVG(t.composite_risk_score) AS avg_risk_score,
  SUM(CASE WHEN t.composite_risk_score > 0.85 THEN 1 ELSE 0 END) AS critical_risk_count,
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) AS total_declines,
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS decline_rate,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) AS security_violations,
  SUM(t.amount) AS total_volume_usd,
  AVG(t.amount) AS avg_transaction_size,
  -- Risk factors
  AVG(CASE WHEN t.is_cross_border THEN 1 ELSE 0 END) * 100 AS pct_cross_border,
  AVG(CASE WHEN t.is_high_value = 1 THEN 1 ELSE 0 END) * 100 AS pct_high_value,
  -- Recommended solutions
  SUM(CASE WHEN t.recommended_solution_name LIKE '%3DS%' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_using_3ds,
  SUM(CASE WHEN t.recommended_solution_name LIKE '%Antifraud%' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_using_antifraud
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
  AND t.composite_risk_score > 0.60  -- Focus on medium-high to critical risk
GROUP BY m.mcc_description, m.merchant_cluster, m.mcc
HAVING COUNT(*) >= 50  -- Minimum volume for statistical significance
ORDER BY avg_risk_score DESC, critical_risk_count DESC
LIMIT 50;

-- Visualization Type: Table with conditional formatting
-- Columns: All fields
-- Conditional formatting: 
--   - avg_risk_score: Red gradient (higher = darker)
--   - decline_rate: Red gradient
--   - pct_using_3ds: Green gradient (higher = better)

SELECT * FROM payments_lakehouse.gold.dashboard_high_risk_industries;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 5: Risk Score Trend (Last 7 Days)

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_risk_trend AS
SELECT 
  DATE_TRUNC('day', t.timestamp) AS date,
  m.mcc_description AS merchant_sector,
  AVG(t.composite_risk_score) AS avg_risk_score,
  AVG(t.cardholder_risk_score) AS avg_cardholder_risk,
  AVG(t.merchant_risk_score) AS avg_merchant_risk,
  AVG(t.country_risk_score) AS avg_country_risk,
  AVG(t.sector_risk_score) AS avg_sector_risk,
  COUNT(*) AS transaction_count,
  SUM(t.amount) AS daily_volume
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY date, m.mcc_description
ORDER BY date, m.mcc_description;

-- Visualization Type: Line Chart
-- X-axis: date
-- Y-axis: avg_risk_score
-- Multiple lines by: merchant_sector
-- Secondary Y-axis: transaction_count

SELECT * FROM payments_lakehouse.gold.dashboard_risk_trend;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 6: Risk Mitigation Effectiveness

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_risk_mitigation AS
SELECT 
  m.mcc_description AS merchant_sector,
  t.recommended_solution_name AS solution_stack,
  -- Overall metrics
  COUNT(*) AS total_transactions,
  AVG(t.composite_risk_score) AS avg_risk_score_before_mitigation,
  AVG(CASE WHEN t.is_approved THEN t.composite_risk_score END) AS avg_risk_score_approved,
  -- Approval metrics
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  -- Fraud metrics
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) AS fraud_attempts_blocked,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS fraud_block_rate,
  -- Cost metrics
  AVG(t.solution_cost) AS avg_cost_per_transaction,
  SUM(t.amount) AS total_volume_processed
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
  AND t.composite_risk_score > 0.50  -- Focus on higher risk transactions
GROUP BY m.mcc_description, t.recommended_solution_name
HAVING COUNT(*) >= 20
ORDER BY m.mcc_description, avg_risk_score_before_mitigation DESC;

-- Visualization Type: Grouped Bar Chart
-- X-axis: merchant_sector
-- Y-axis: approval_rate
-- Group by: chosen_solution_stack
-- Color: fraud_block_rate

SELECT * FROM payments_lakehouse.gold.dashboard_risk_mitigation;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 7: External Risk Signal Impact

-- COMMAND ----------

-- DBTITLE 1,Cell 15
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_external_risk_impact AS
SELECT 
  m.mcc_description AS merchant_sector,
  t.cardholder_country AS geography,
  -- External risk factors (from joined table)
  AVG(t.sector_risk_score) AS avg_sector_risk,
  AVG(t.country_risk_score) AS avg_country_risk,
  SUM(CASE WHEN t.aml_risk_level = 'HIGH' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_high_aml_risk,
  -- Transaction outcomes
  COUNT(*) AS transaction_count,
  AVG(t.composite_risk_score) AS avg_combined_risk_score,
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS decline_rate,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS fraud_rate,
  -- Volume
  SUM(t.amount) AS total_volume
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
  AND t.country_risk_score IS NOT NULL
  AND t.sector_risk_score IS NOT NULL
GROUP BY m.mcc_description, t.cardholder_country
ORDER BY avg_combined_risk_score DESC;

-- Visualization Type: Scatter Plot
-- X-axis: avg_sector_risk
-- Y-axis: decline_rate
-- Size: transaction_count
-- Color: merchant_sector
-- Tooltip: geography, pct_high_aml_risk, total_volume

SELECT * FROM payments_lakehouse.gold.dashboard_external_risk_impact;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 8: Risk Score Summary KPIs

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_risk_kpis AS
SELECT 
  -- Overall risk metrics
  AVG(t.composite_risk_score) AS overall_avg_risk_score,
  PERCENTILE(t.composite_risk_score, 0.50) AS median_risk_score,
  PERCENTILE(t.composite_risk_score, 0.90) AS p90_risk_score,
  PERCENTILE(t.composite_risk_score, 0.95) AS p95_risk_score,
  PERCENTILE(t.composite_risk_score, 0.99) AS p99_risk_score,
  
  -- Risk distribution
  SUM(CASE WHEN t.composite_risk_score < 0.3 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_low_risk,
  SUM(CASE WHEN t.composite_risk_score BETWEEN 0.3 AND 0.6 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_medium_risk,
  SUM(CASE WHEN t.composite_risk_score BETWEEN 0.6 AND 0.85 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_high_risk,
  SUM(CASE WHEN t.composite_risk_score > 0.85 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_critical_risk,
  
  -- High-risk transactions
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN 1 ELSE 0 END) AS high_risk_transaction_count,
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN t.amount ELSE 0 END) AS high_risk_volume_usd,
  
  -- Fraud indicators
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) AS security_violations,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS fraud_attempt_rate,
  
  -- Total counts
  COUNT(*) AS total_transactions,
  COUNT(DISTINCT t.merchant_id) AS unique_merchants,
  
  -- Timestamp
  MAX(t.timestamp) AS last_updated
FROM payments_lakehouse.silver.payments_enriched_stream t
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS;

-- Visualization Type: Counter/KPI Cards
-- Display each metric as a separate KPI card

SELECT * FROM payments_lakehouse.gold.dashboard_risk_kpis;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Dashboard Layout Recommendations
-- MAGIC
-- MAGIC **Page 1: Risk Overview**
-- MAGIC - Top: 4 KPI cards (Query 8: avg risk, p90, high-risk count, fraud rate)
-- MAGIC - Middle Left: Bar chart (Query 1: Risk by sector)
-- MAGIC - Middle Right: Stacked bar (Query 2: Risk distribution)
-- MAGIC - Bottom: Line chart (Query 5: Risk trend)
-- MAGIC
-- MAGIC **Page 2: Industry Analysis**
-- MAGIC - Top: Heatmap (Query 3: Sector risk hourly)
-- MAGIC - Middle: Table (Query 4: High-risk industries)
-- MAGIC - Bottom Left: Grouped bar (Query 6: Mitigation effectiveness)
-- MAGIC - Bottom Right: Scatter (Query 7: External risk impact)
-- MAGIC
-- MAGIC **Filters:**
-- MAGIC - Date range (default: last 7 days)
-- MAGIC - Merchant sector (multi-select)
-- MAGIC - Geography (multi-select)
-- MAGIC - Risk threshold (slider: 0.0 - 1.0)
-- MAGIC
-- MAGIC **Refresh Rate:** Every 5 minutes
