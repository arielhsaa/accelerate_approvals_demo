-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Dashboard 2: Transaction Volume Analysis by Country
-- MAGIC 
-- MAGIC **Purpose:** Monitor global transaction patterns, identify growth opportunities, and track regional performance metrics.
-- MAGIC 
-- MAGIC **Key Metrics:**
-- MAGIC - Transaction volume by country
-- MAGIC - Geographic distribution
-- MAGIC - Cross-border transaction patterns
-- MAGIC - Country-specific approval rates
-- MAGIC - Regional growth trends

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 1: Global Transaction Volume Map

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_transactions_by_country AS
SELECT 
  t.cardholder_country AS country,
  c.country_code,
  c.country_name,
  c.region,
  c.continent,
  -- Transaction counts
  COUNT(DISTINCT t.transaction_id) AS total_transactions,
  COUNT(DISTINCT t.cardholder_id) AS unique_cardholders,
  COUNT(DISTINCT t.merchant_id) AS unique_merchants,
  -- Transaction types
  SUM(CASE WHEN t.is_cross_border THEN 1 ELSE 0 END) AS cross_border_transactions,
  SUM(CASE WHEN t.is_cross_border THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_cross_border,
  -- Volume metrics
  SUM(t.amount) AS total_volume_usd,
  AVG(t.amount) AS avg_transaction_amount,
  PERCENTILE(t.amount, 0.50) AS median_transaction_amount,
  PERCENTILE(t.amount, 0.90) AS p90_transaction_amount,
  -- Approval metrics
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) AS approved_count,
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  -- Channel breakdown
  SUM(CASE WHEN t.channel = 'ecommerce' THEN 1 ELSE 0 END) AS online_transactions,
  SUM(CASE WHEN t.channel = 'moto' THEN 1 ELSE 0 END) AS mobile_transactions,
  SUM(CASE WHEN t.channel = 'pos' THEN 1 ELSE 0 END) AS pos_transactions,
  -- Risk metrics
  AVG(t.composite_risk_score) AS avg_risk_score,
  SUM(CASE WHEN t.composite_risk_score > 0.75 THEN 1 ELSE 0 END) AS high_risk_transactions,
  -- Growth metrics
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 1 DAY THEN 1 END) AS transactions_last_24h,
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS AND t.timestamp < current_timestamp() - INTERVAL 6 DAYS THEN 1 END) AS transactions_7_days_ago
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.cardholders_dim c ON t.cardholder_id = c.cardholder_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY t.cardholder_country, c.country_code, c.country_name, c.region, c.continent
ORDER BY total_volume_usd DESC;

-- Visualization Type: Choropleth Map
-- Geographic field: country_code
-- Color intensity: total_volume_usd
-- Tooltip: country_name, total_transactions, approval_rate, avg_transaction_amount

SELECT * FROM payments_lakehouse.gold.dashboard_transactions_by_country;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 2: Top 20 Countries by Transaction Volume

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_top_countries AS
SELECT 
  t.cardholder_country AS country,
  c.country_name,
  -- Current period (last 7 days)
  COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END) AS transactions_current_week,
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) AS volume_current_week_usd,
  -- Previous period (7-14 days ago)
  COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END) AS transactions_previous_week,
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) AS volume_previous_week_usd,
  -- Growth calculations
  ROUND((COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END) - 
         COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END)) /
         NULLIF(COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END), 0) * 100, 2) AS transaction_growth_pct,
  ROUND((SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) -
         SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END)) /
         NULLIF(SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END), 0) * 100, 2) AS volume_growth_pct,
  -- Performance metrics
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS AND t.is_approved THEN 1 ELSE 0 END) / 
    NULLIF(COUNT(DISTINCT CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.transaction_id END), 0) * 100 AS approval_rate_current_week,
  AVG(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount END) AS avg_transaction_size_current_week
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.cardholders_dim c ON t.cardholder_id = c.cardholder_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 14 DAYS
GROUP BY t.cardholder_country, c.country_name
HAVING transactions_current_week > 0
ORDER BY volume_current_week_usd DESC
LIMIT 20;

-- Visualization Type: Horizontal Bar Chart with trend indicators
-- X-axis: volume_current_week_usd
-- Y-axis: country_name
-- Color: volume_growth_pct (green for positive, red for negative)
-- Add arrows for growth direction

SELECT * FROM payments_lakehouse.gold.dashboard_top_countries;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 3: Daily Transaction Trend by Country (Top 10)

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_country_daily_trend AS
WITH top_countries AS (
  SELECT cardholder_country, SUM(amount) AS total_volume
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
  GROUP BY cardholder_country
  ORDER BY total_volume DESC
  LIMIT 10
)
SELECT 
  DATE_TRUNC('day', t.timestamp) AS date,
  t.cardholder_country AS country,
  COUNT(DISTINCT t.transaction_id) AS transaction_count,
  SUM(t.amount) AS daily_volume_usd,
  AVG(t.amount) AS avg_transaction_amount,
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  COUNT(DISTINCT t.cardholder_id) AS unique_cardholders,
  COUNT(DISTINCT t.merchant_id) AS unique_merchants,
  -- Moving averages
  AVG(SUM(t.amount)) OVER (PARTITION BY t.cardholder_country ORDER BY DATE_TRUNC('day', t.timestamp) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS volume_7day_ma,
  AVG(COUNT(DISTINCT t.transaction_id)) OVER (PARTITION BY t.cardholder_country ORDER BY DATE_TRUNC('day', t.timestamp) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS transactions_7day_ma
FROM payments_lakehouse.silver.payments_enriched_stream t
WHERE t.timestamp >= current_timestamp() - INTERVAL 30 DAYS
  AND t.cardholder_country IN (SELECT cardholder_country FROM top_countries)
GROUP BY date, t.cardholder_country
ORDER BY date DESC, t.cardholder_country;

-- Visualization Type: Multi-line Chart
-- X-axis: date
-- Y-axis: transaction_count
-- Multiple lines: One per country
-- Optional secondary Y-axis: daily_volume_usd

SELECT * FROM payments_lakehouse.gold.dashboard_country_daily_trend;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 4: Cross-Border Transaction Analysis

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_cross_border_flow AS
SELECT 
  c.country_name AS origin_country,
  t.cardholder_country AS origin_geography,
  t.merchant_country AS destination_country,
  -- Transaction metrics
  COUNT(DISTINCT t.transaction_id) AS cross_border_transactions,
  SUM(t.amount) AS total_volume_usd,
  AVG(t.amount) AS avg_transaction_amount,
  -- Performance metrics
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  AVG(t.composite_risk_score) AS avg_risk_score,
  -- Decline analysis
  SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) AS decline_count,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) AS security_violations,
  -- Solution usage
  SUM(CASE WHEN t.recommended_solution_name LIKE '%3DS%' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_using_3ds,
  SUM(CASE WHEN t.recommended_solution_name LIKE '%Antifraud%' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_using_antifraud,
  -- Popular corridors
  COUNT(*) AS transaction_rank
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.cardholders_dim c ON t.cardholder_id = c.cardholder_id
WHERE t.is_cross_border = TRUE
  AND t.timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY origin_country, t.cardholder_country, t.merchant_country
HAVING COUNT(*) >= 10  -- Minimum threshold for statistical significance
ORDER BY total_volume_usd DESC
LIMIT 50;

-- Visualization Type: Sankey Diagram or Chord Diagram
-- Source: origin_country
-- Target: destination_country
-- Flow width: total_volume_usd
-- Color: approval_rate (red to green gradient)

SELECT * FROM payments_lakehouse.gold.dashboard_cross_border_flow;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 5: Regional Performance Comparison

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_regional_performance AS
SELECT 
  c.region,
  c.continent,
  -- Transaction counts
  COUNT(DISTINCT t.transaction_id) AS total_transactions,
  COUNT(DISTINCT t.cardholder_id) AS unique_cardholders,
  COUNT(DISTINCT t.merchant_id) AS unique_merchants,
  -- Volume metrics
  SUM(t.amount) AS total_volume_usd,
  AVG(t.amount) AS avg_transaction_amount,
  -- Approval metrics
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  -- Channel distribution
  SUM(CASE WHEN t.channel = 'ecommerce' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_online,
  SUM(CASE WHEN t.channel = 'moto' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_mobile,
  SUM(CASE WHEN t.channel = 'pos' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_pos,
  -- Risk and fraud
  AVG(t.composite_risk_score) AS avg_risk_score,
  SUM(CASE WHEN t.reason_code = '63_SECURITY_VIOLATION' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS fraud_rate,
  -- Cross-border
  SUM(CASE WHEN t.is_cross_border THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_cross_border,
  -- Growth (WoW)
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_this_week,
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_last_week,
  ROUND((COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) -
         COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END)) /
         NULLIF(COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END), 0) * 100, 2) AS wow_growth_pct
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.cardholders_dim c ON t.cardholder_id = c.cardholder_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY c.region, c.continent
ORDER BY total_volume_usd DESC;

-- Visualization Type: Grouped Bar Chart
-- X-axis: region
-- Y-axis: approval_rate, avg_risk_score, pct_cross_border
-- Multiple bars per region showing different metrics

SELECT * FROM payments_lakehouse.gold.dashboard_regional_performance;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 6: Country Transaction Breakdown by Channel & Payment Method

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_country_channel_breakdown AS
SELECT 
  t.cardholder_country AS country,
  t.channel,
  t.card_network AS payment_method,
  -- Transaction counts
  COUNT(DISTINCT t.transaction_id) AS transaction_count,
  SUM(t.amount) AS total_volume_usd,
  AVG(t.amount) AS avg_transaction_amount,
  -- Performance
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  -- Market share within country
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY t.cardholder_country) AS pct_of_country_volume,
  -- Risk
  AVG(t.composite_risk_score) AS avg_risk_score,
  -- Solution usage
  MAX(t.recommended_solution_name) AS most_common_solution
FROM payments_lakehouse.silver.payments_enriched_stream t
WHERE t.timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY t.cardholder_country, t.channel, t.card_network
HAVING COUNT(*) >= 5
ORDER BY t.cardholder_country, transaction_count DESC;

-- Visualization Type: Stacked Bar Chart
-- X-axis: country (top 15 by volume)
-- Y-axis: transaction_count
-- Stack by: channel
-- Color: payment_method

SELECT * FROM payments_lakehouse.gold.dashboard_country_channel_breakdown
WHERE country IN (
  SELECT cardholder_country FROM (
    SELECT cardholder_country, SUM(amount) AS vol 
    FROM payments_lakehouse.silver.payments_enriched_stream 
    WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
    GROUP BY cardholder_country ORDER BY vol DESC LIMIT 15
  )
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 7: Hourly Transaction Patterns by Country

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_country_hourly_pattern AS
SELECT 
  t.cardholder_country AS country,
  EXTRACT(HOUR FROM t.timestamp) AS hour_of_day,
  CASE 
    WHEN EXTRACT(HOUR FROM t.timestamp) BETWEEN 6 AND 11 THEN 'Morning'
    WHEN EXTRACT(HOUR FROM t.timestamp) BETWEEN 12 AND 17 THEN 'Afternoon'
    WHEN EXTRACT(HOUR FROM t.timestamp) BETWEEN 18 AND 22 THEN 'Evening'
    ELSE 'Night'
  END AS time_period,
  -- Transaction metrics
  COUNT(DISTINCT t.transaction_id) AS transaction_count,
  AVG(t.amount) AS avg_transaction_amount,
  SUM(t.amount) AS total_volume_usd,
  -- Performance
  SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) / COUNT(*) * 100 AS approval_rate,
  AVG(t.composite_risk_score) AS avg_risk_score,
  -- Peak identification
  COUNT(*) AS transactions_this_hour
FROM payments_lakehouse.silver.payments_enriched_stream t
WHERE t.timestamp >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY t.cardholder_country, hour_of_day, time_period
ORDER BY t.cardholder_country, hour_of_day;

-- Visualization Type: Heatmap
-- X-axis: hour_of_day
-- Y-axis: country (top 10)
-- Color intensity: transaction_count
-- Tooltip: approval_rate, avg_transaction_amount

SELECT * FROM payments_lakehouse.gold.dashboard_country_hourly_pattern
WHERE country IN (
  SELECT cardholder_country FROM (
    SELECT cardholder_country, COUNT(*) AS cnt 
    FROM payments_lakehouse.silver.payments_enriched_stream 
    WHERE timestamp >= current_timestamp() - INTERVAL 7 DAYS
    GROUP BY cardholder_country ORDER BY cnt DESC LIMIT 10
  )
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 8: Country Performance KPIs

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_country_kpis AS
SELECT 
  -- Global totals
  COUNT(DISTINCT cardholder_country) AS total_countries,
  COUNT(DISTINCT transaction_id) AS total_global_transactions,
  SUM(amount) AS total_global_volume_usd,
  AVG(amount) AS global_avg_transaction_amount,
  
  -- Top performers
  (SELECT cardholder_country FROM payments_lakehouse.silver.payments_enriched_stream 
   WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
   GROUP BY cardholder_country ORDER BY SUM(amount) DESC LIMIT 1) AS top_country_by_volume,
  
  (SELECT SUM(amount) FROM payments_lakehouse.silver.payments_enriched_stream 
   WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
   AND cardholder_country = (
     SELECT cardholder_country FROM payments_lakehouse.silver.payments_enriched_stream 
     WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
     GROUP BY cardholder_country ORDER BY SUM(amount) DESC LIMIT 1
   )) AS top_country_volume_usd,
  
  -- Cross-border metrics
  SUM(CASE WHEN is_cross_border THEN 1 ELSE 0 END) AS total_cross_border_transactions,
  SUM(CASE WHEN is_cross_border THEN 1 ELSE 0 END) / COUNT(*) * 100 AS pct_cross_border,
  SUM(CASE WHEN is_cross_border THEN amount ELSE 0 END) AS cross_border_volume_usd,
  
  -- Growth metrics
  COUNT(CASE WHEN timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_last_7_days,
  COUNT(CASE WHEN timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_previous_7_days,
  ROUND((COUNT(CASE WHEN timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) -
         COUNT(CASE WHEN timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END)) /
         NULLIF(COUNT(CASE WHEN timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END), 0) * 100, 2) AS wow_growth_pct,
  
  -- Timestamp
  MAX(timestamp) AS last_updated
FROM payments_lakehouse.silver.payments_enriched_stream
WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS;

-- Visualization Type: KPI Cards
-- Display each metric as a separate counter/card

SELECT * FROM payments_lakehouse.gold.dashboard_country_kpis;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 9: Fastest Growing Countries

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_fastest_growing_countries AS
SELECT 
  t.cardholder_country AS country,
  c.country_name,
  c.region,
  -- Current period metrics
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_current_week,
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) AS volume_current_week,
  -- Previous period metrics
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transactions_previous_week,
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
       AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) AS volume_previous_week,
  -- Growth calculations
  ROUND((COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) -
         COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END)) /
         NULLIF(COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END), 0) * 100, 2) AS transaction_growth_pct,
  ROUND((SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) -
         SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END)) /
         NULLIF(SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
         AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END), 0) * 100, 2) AS volume_growth_pct,
  -- Absolute growth
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN 1 END) -
  COUNT(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
   AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN 1 END) AS transaction_growth_absolute,
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) -
  SUM(CASE WHEN t.timestamp >= current_timestamp() - INTERVAL 14 DAYS 
   AND t.timestamp < current_timestamp() - INTERVAL 7 DAYS THEN t.amount ELSE 0 END) AS volume_growth_absolute
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.cardholders_dim c ON t.cardholder_id = c.cardholder_id
WHERE t.timestamp >= current_timestamp() - INTERVAL 14 DAYS
GROUP BY t.cardholder_country, c.country_name, c.region
HAVING transactions_current_week >= 10  -- Minimum threshold
ORDER BY transaction_growth_pct DESC
LIMIT 20;

-- Visualization Type: Waterfall Chart or Bubble Chart
-- X-axis: transaction_growth_pct
-- Y-axis: volume_growth_absolute
-- Size: transactions_current_week
-- Color: region

SELECT * FROM payments_lakehouse.gold.dashboard_fastest_growing_countries;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Dashboard Layout Recommendations
-- MAGIC 
-- MAGIC **Page 1: Global Overview**
-- MAGIC - Top: 4 KPI cards (Query 8: Total countries, transactions, volume, WoW growth)
-- MAGIC - Center: Large choropleth map (Query 1: Transactions by country)
-- MAGIC - Bottom: Horizontal bar chart (Query 2: Top 20 countries)
-- MAGIC 
-- MAGIC **Page 2: Country Performance**
-- MAGIC - Top: Multi-line chart (Query 3: Daily trend by top 10 countries)
-- MAGIC - Middle Left: Stacked bar (Query 6: Channel breakdown by country)
-- MAGIC - Middle Right: Table (Query 9: Fastest growing countries)
-- MAGIC - Bottom: Heatmap (Query 7: Hourly patterns)
-- MAGIC 
-- MAGIC **Page 3: Cross-Border Analysis**
-- MAGIC - Top: Sankey diagram (Query 4: Cross-border flow)
-- MAGIC - Bottom Left: Grouped bar (Query 5: Regional performance)
-- MAGIC - Bottom Right: Statistics table (cross-border metrics)
-- MAGIC 
-- MAGIC **Filters:**
-- MAGIC - Date range (default: last 30 days)
-- MAGIC - Country/Region (multi-select with search)
-- MAGIC - Channel (online, mobile, pos)
-- MAGIC - Transaction amount range
-- MAGIC - Cross-border flag (yes/no/all)
-- MAGIC 
-- MAGIC **Refresh Rate:** Every 5 minutes
-- MAGIC 
-- MAGIC **Export Options:**
-- MAGIC - CSV export for all queries
-- MAGIC - PDF dashboard snapshot
-- MAGIC - Email scheduled reports
