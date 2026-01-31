-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Dashboard 3: Standard vs Optimized Approval Rates
-- MAGIC 
-- MAGIC **Purpose:** Compare baseline approval rates against Smart Checkout optimized rates to demonstrate business impact and ROI of payment optimization strategies.
-- MAGIC 
-- MAGIC **Key Metrics:**
-- MAGIC - Approval rate uplift from optimization
-- MAGIC - Revenue impact of Smart Checkout
-- MAGIC - Solution mix effectiveness
-- MAGIC - A/B test results
-- MAGIC - ROI calculations

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 1: Approval Rate Comparison Overview

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_approval_rate_comparison AS
WITH baseline_metrics AS (
  -- Baseline: No smart routing, basic processing
  SELECT 
    COUNT(*) AS total_transactions_baseline,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS approved_baseline,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate_baseline,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume_baseline,
    SUM(amount) AS total_volume_baseline
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
    AND (chosen_solution_stack = 'Antifraud' OR chosen_solution_stack = 'DataShareOnly')  -- Basic solutions only
),
optimized_metrics AS (
  -- Optimized: Smart Checkout with advanced solution combinations
  SELECT 
    COUNT(*) AS total_transactions_optimized,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS approved_optimized,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate_optimized,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume_optimized,
    SUM(amount) AS total_volume_optimized
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
    AND chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly')  -- Advanced smart routing
),
all_transactions AS (
  SELECT 
    COUNT(*) AS total_transactions_all,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate_all,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume_all
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
)
SELECT 
  -- Baseline metrics
  b.total_transactions_baseline,
  b.approval_rate_baseline,
  b.approved_volume_baseline,
  
  -- Optimized metrics
  o.total_transactions_optimized,
  o.approval_rate_optimized,
  o.approved_volume_optimized,
  
  -- Overall metrics
  a.total_transactions_all,
  a.approval_rate_all,
  a.approved_volume_all,
  
  -- Uplift calculations
  ROUND(o.approval_rate_optimized - b.approval_rate_baseline, 2) AS approval_rate_uplift_pct,
  ROUND((o.approval_rate_optimized - b.approval_rate_baseline) / b.approval_rate_baseline * 100, 2) AS approval_rate_improvement_pct,
  
  -- Revenue impact
  o.approved_volume_optimized - b.approved_volume_baseline AS incremental_revenue_usd,
  ROUND((o.approved_volume_optimized - b.approved_volume_baseline) / b.approved_volume_baseline * 100, 2) AS revenue_uplift_pct,
  
  -- Projected annual impact
  (o.approved_volume_optimized - b.approved_volume_baseline) * 12 AS projected_annual_revenue_gain,
  
  -- Last updated
  current_timestamp() AS last_updated
FROM baseline_metrics b
CROSS JOIN optimized_metrics o
CROSS JOIN all_transactions a;

-- Visualization Type: KPI Cards and Comparison Bars
-- Display: Before/After comparison with uplift percentage

SELECT * FROM payments_lakehouse.gold.dashboard_approval_rate_comparison;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 2: Approval Rate Uplift by Segment

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_uplift_by_segment AS
WITH segmented_performance AS (
  SELECT 
    geography,
    channel,
    merchant_category,
    CASE 
      WHEN amount < 50 THEN '0-50'
      WHEN amount < 500 THEN '50-500'
      WHEN amount < 2500 THEN '500-2500'
      ELSE '2500+'
    END AS amount_range,
    chosen_solution_stack,
    CASE 
      WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 'Baseline'
      ELSE 'Optimized'
    END AS optimization_type,
    COUNT(*) AS transaction_count,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS approved_count,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume,
    AVG(risk_score) AS avg_risk_score,
    AVG(predicted_approval_probability) AS avg_predicted_approval_probability
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
  GROUP BY geography, channel, merchant_category, amount_range, chosen_solution_stack, optimization_type
)
SELECT 
  s1.geography,
  s1.channel,
  s1.merchant_category,
  s1.amount_range,
  -- Baseline metrics
  s1.transaction_count AS baseline_transaction_count,
  s1.approval_rate AS baseline_approval_rate,
  s1.approved_volume AS baseline_approved_volume,
  -- Optimized metrics
  s2.transaction_count AS optimized_transaction_count,
  s2.approval_rate AS optimized_approval_rate,
  s2.approved_volume AS optimized_approved_volume,
  -- Uplift calculations
  ROUND(s2.approval_rate - s1.approval_rate, 2) AS approval_rate_uplift_pct,
  ROUND((s2.approval_rate - s1.approval_rate) / s1.approval_rate * 100, 2) AS approval_rate_improvement_pct,
  s2.approved_volume - s1.approved_volume AS incremental_revenue_usd,
  -- Risk comparison
  s1.avg_risk_score AS baseline_avg_risk_score,
  s2.avg_risk_score AS optimized_avg_risk_score,
  -- ML model accuracy
  s2.avg_predicted_approval_probability AS predicted_success_rate
FROM segmented_performance s1
JOIN segmented_performance s2 
  ON s1.geography = s2.geography
  AND s1.channel = s2.channel
  AND s1.merchant_category = s2.merchant_category
  AND s1.amount_range = s2.amount_range
WHERE s1.optimization_type = 'Baseline'
  AND s2.optimization_type = 'Optimized'
  AND s1.transaction_count >= 10  -- Minimum threshold for statistical significance
  AND s2.transaction_count >= 10
ORDER BY approval_rate_improvement_pct DESC;

-- Visualization Type: Grouped Bar Chart
-- X-axis: Segments (geography, channel, amount_range)
-- Y-axis: approval_rate
-- Bars: Baseline vs Optimized side-by-side
-- Color: Green for optimized, Grey for baseline

SELECT * FROM payments_lakehouse.gold.dashboard_uplift_by_segment;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 3: Solution Mix Performance Comparison

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_solution_performance AS
SELECT 
  chosen_solution_stack,
  CASE 
    WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 'Baseline'
    WHEN chosen_solution_stack LIKE '%3DS%' AND chosen_solution_stack LIKE '%NetworkToken%' THEN 'Advanced Combo'
    WHEN chosen_solution_stack LIKE '%3DS%' THEN 'Enhanced Security'
    WHEN chosen_solution_stack LIKE '%NetworkToken%' THEN 'Token Optimized'
    ELSE 'Other Optimized'
  END AS solution_category,
  -- Transaction metrics
  COUNT(*) AS total_transactions,
  SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS approved_transactions,
  SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate,
  -- Volume metrics
  SUM(amount) AS total_volume_usd,
  SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume_usd,
  AVG(amount) AS avg_transaction_amount,
  -- Risk metrics
  AVG(risk_score) AS avg_risk_score,
  SUM(CASE WHEN risk_score > 0.75 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_high_risk,
  -- Cost metrics (simulated based on solution complexity)
  CASE 
    WHEN chosen_solution_stack = 'DataShareOnly' THEN 0.05
    WHEN chosen_solution_stack = 'Antifraud' THEN 0.10
    WHEN chosen_solution_stack LIKE '%3DS%' AND chosen_solution_stack LIKE '%Antifraud%' AND chosen_solution_stack LIKE '%IDPay%' THEN 0.45
    WHEN chosen_solution_stack LIKE '%3DS%' AND chosen_solution_stack LIKE '%NetworkToken%' THEN 0.23
    WHEN chosen_solution_stack LIKE '%3DS%' THEN 0.15
    WHEN chosen_solution_stack LIKE '%NetworkToken%' THEN 0.08
    WHEN chosen_solution_stack LIKE '%Passkey%' THEN 0.12
    ELSE 0.15
  END AS cost_per_transaction_usd,
  -- ROI calculation
  (SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) - 
   (COUNT(*) * CASE 
     WHEN chosen_solution_stack = 'DataShareOnly' THEN 0.05
     WHEN chosen_solution_stack = 'Antifraud' THEN 0.10
     WHEN chosen_solution_stack LIKE '%3DS%' AND chosen_solution_stack LIKE '%Antifraud%' AND chosen_solution_stack LIKE '%IDPay%' THEN 0.45
     WHEN chosen_solution_stack LIKE '%3DS%' AND chosen_solution_stack LIKE '%NetworkToken%' THEN 0.23
     WHEN chosen_solution_stack LIKE '%3DS%' THEN 0.15
     WHEN chosen_solution_stack LIKE '%NetworkToken%' THEN 0.08
     WHEN chosen_solution_stack LIKE '%Passkey%' THEN 0.12
     ELSE 0.15
   END)) AS net_revenue_usd,
  -- Decline analysis
  SUM(CASE WHEN approval_status = 'declined' THEN 1 ELSE 0 END) AS decline_count,
  SUM(CASE WHEN approval_status = 'declined' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS decline_rate,
  -- Most common decline reasons
  MAX(CASE WHEN approval_status = 'declined' THEN reason_code END) AS top_decline_reason
FROM payments_lakehouse.silver.payments_enriched_stream
WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY chosen_solution_stack, solution_category
HAVING COUNT(*) >= 20
ORDER BY approval_rate DESC, total_transactions DESC;

-- Visualization Type: Scatter Plot
-- X-axis: cost_per_transaction_usd
-- Y-axis: approval_rate
-- Size: total_transactions
-- Color: solution_category
-- Quadrant analysis: High approval/Low cost (ideal), etc.

SELECT * FROM payments_lakehouse.gold.dashboard_solution_performance;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 4: Time Series - Approval Rate Trend (Baseline vs Optimized)

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_approval_trend_comparison AS
SELECT 
  DATE_TRUNC('hour', timestamp) AS time_bucket,
  -- Baseline transactions
  COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS baseline_transaction_count,
  SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0) AS baseline_approval_rate,
  -- Optimized transactions
  COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS optimized_transaction_count,
  SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0) AS optimized_approval_rate,
  -- Overall
  COUNT(*) AS total_transaction_count,
  SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS overall_approval_rate,
  -- Volume
  SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS baseline_approved_volume,
  SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS optimized_approved_volume,
  -- Moving averages (3-hour window)
  AVG(SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0)) 
    OVER (ORDER BY DATE_TRUNC('hour', timestamp) ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS baseline_approval_rate_ma3,
  AVG(SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0))
    OVER (ORDER BY DATE_TRUNC('hour', timestamp) ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS optimized_approval_rate_ma3
FROM payments_lakehouse.silver.payments_enriched_stream
WHERE timestamp >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY time_bucket
ORDER BY time_bucket DESC;

-- Visualization Type: Dual-line Chart with shaded area between
-- X-axis: time_bucket
-- Y-axis: approval_rate
-- Line 1: baseline_approval_rate (grey)
-- Line 2: optimized_approval_rate (green)
-- Shaded area: Gap between lines (represents uplift)
-- Optional: Moving average lines for smoothing

SELECT * FROM payments_lakehouse.gold.dashboard_approval_trend_comparison;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 5: Revenue Impact Analysis

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_revenue_impact AS
WITH daily_metrics AS (
  SELECT 
    DATE_TRUNC('day', timestamp) AS date,
    -- Baseline metrics
    SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS baseline_approved_volume,
    COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS baseline_transaction_count,
    -- Optimized metrics
    SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS optimized_approved_volume,
    COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS optimized_transaction_count,
    -- Processing costs (estimated)
    SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 0.10 ELSE 0.20 END) AS processing_costs
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
  GROUP BY date
)
SELECT 
  date,
  baseline_approved_volume,
  optimized_approved_volume,
  baseline_transaction_count,
  optimized_transaction_count,
  processing_costs,
  -- Revenue uplift
  optimized_approved_volume - baseline_approved_volume AS daily_revenue_uplift,
  (optimized_approved_volume - baseline_approved_volume) * 30 AS projected_monthly_uplift,
  (optimized_approved_volume - baseline_approved_volume) * 365 AS projected_annual_uplift,
  -- Net benefit (revenue uplift minus additional processing costs)
  (optimized_approved_volume - baseline_approved_volume) - processing_costs AS net_daily_benefit,
  ((optimized_approved_volume - baseline_approved_volume) - processing_costs) * 30 AS net_monthly_benefit,
  ((optimized_approved_volume - baseline_approved_volume) - processing_costs) * 365 AS net_annual_benefit,
  -- Cumulative impact
  SUM(optimized_approved_volume - baseline_approved_volume) OVER (ORDER BY date) AS cumulative_revenue_uplift,
  SUM((optimized_approved_volume - baseline_approved_volume) - processing_costs) OVER (ORDER BY date) AS cumulative_net_benefit,
  -- ROI calculation
  CASE 
    WHEN processing_costs > 0 
    THEN ((optimized_approved_volume - baseline_approved_volume) / processing_costs - 1) * 100
    ELSE NULL 
  END AS daily_roi_pct
FROM daily_metrics
ORDER BY date DESC;

-- Visualization Type: Area Chart with dual Y-axis
-- X-axis: date
-- Primary Y-axis: daily_revenue_uplift (area chart, green gradient)
-- Secondary Y-axis: cumulative_revenue_uplift (line chart, dark green)
-- Add annotation line for break-even point

SELECT * FROM payments_lakehouse.gold.dashboard_revenue_impact;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 6: Geography-wise Approval Uplift

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_geo_approval_uplift AS
SELECT 
  geography,
  -- Baseline metrics
  COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS baseline_transactions,
  SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0) AS baseline_approval_rate,
  SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS baseline_approved_volume,
  -- Optimized metrics
  COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END) AS optimized_transactions,
  SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0) AS optimized_approval_rate,
  SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS optimized_approved_volume,
  -- Uplift calculations
  (SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0)) -
  (SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / 
    NULLIF(COUNT(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 1 END), 0)) AS approval_rate_uplift_pct,
  -- Revenue impact
  SUM(CASE WHEN chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) -
  SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') AND approval_status = 'approved' THEN amount ELSE 0 END) AS revenue_uplift_usd,
  -- Most effective solution for this geography
  (SELECT chosen_solution_stack 
   FROM payments_lakehouse.silver.payments_enriched_stream sub
   WHERE sub.geography = main.geography
     AND sub.chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly')
     AND sub.approval_status = 'approved'
   GROUP BY chosen_solution_stack
   ORDER BY COUNT(*) DESC
   LIMIT 1) AS best_performing_solution
FROM payments_lakehouse.silver.payments_enriched_stream main
WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
GROUP BY geography
HAVING baseline_transactions >= 20 AND optimized_transactions >= 20
ORDER BY approval_rate_uplift_pct DESC;

-- Visualization Type: Diverging Bar Chart (Lollipop chart)
-- Y-axis: geography
-- X-axis: approval_rate_uplift_pct (diverging from 0)
-- Color: Green for positive uplift, Red for negative
-- Size of lollipop: revenue_uplift_usd

SELECT * FROM payments_lakehouse.gold.dashboard_geo_approval_uplift;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 7: Cascading Success Rate Analysis

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_cascading_impact AS
WITH initial_attempts AS (
  SELECT 
    transaction_id,
    merchant_id,
    cardholder_id,
    amount,
    geography,
    chosen_solution_stack,
    approval_status,
    reason_code,
    timestamp,
    ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY timestamp) AS attempt_number
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
),
cascaded_attempts AS (
  SELECT 
    i1.transaction_id,
    i1.approval_status AS initial_approval_status,
    i1.chosen_solution_stack AS initial_solution,
    i1.reason_code AS initial_decline_reason,
    i2.approval_status AS cascaded_approval_status,
    i2.chosen_solution_stack AS cascaded_solution,
    i1.amount,
    i1.geography
  FROM initial_attempts i1
  LEFT JOIN initial_attempts i2 
    ON i1.transaction_id = i2.transaction_id 
    AND i2.attempt_number = 2
  WHERE i1.attempt_number = 1
)
SELECT 
  geography,
  initial_decline_reason,
  -- Initial attempt metrics
  COUNT(*) AS total_initial_declines,
  COUNT(CASE WHEN cascaded_approval_status = 'approved' THEN 1 END) AS cascade_successes,
  COUNT(CASE WHEN cascaded_approval_status = 'approved' THEN 1 END) * 100.0 / COUNT(*) AS cascade_success_rate,
  -- Without cascading (baseline)
  0 AS baseline_recovery_rate,  -- Assumes no recovery without cascading
  -- Uplift from cascading
  COUNT(CASE WHEN cascaded_approval_status = 'approved' THEN 1 END) * 100.0 / COUNT(*) AS cascading_uplift_pct,
  -- Revenue recovered
  SUM(CASE WHEN cascaded_approval_status = 'approved' THEN amount ELSE 0 END) AS recovered_revenue_usd,
  SUM(amount) AS potential_recovery_usd,
  SUM(CASE WHEN cascaded_approval_status = 'approved' THEN amount ELSE 0 END) * 100.0 / SUM(amount) AS revenue_recovery_rate,
  -- Solution effectiveness
  MAX(cascaded_solution) AS most_successful_cascade_solution,
  -- Projected annual impact
  SUM(CASE WHEN cascaded_approval_status = 'approved' THEN amount ELSE 0 END) * 12 AS projected_annual_recovery
FROM cascaded_attempts
WHERE initial_approval_status = 'declined'
GROUP BY geography, initial_decline_reason
HAVING COUNT(*) >= 10
ORDER BY cascade_success_rate DESC;

-- Visualization Type: Waterfall Chart
-- Shows revenue flow: Initial Declines → Cascade Attempts → Recovered → Still Declined
-- Color code: Red for declines, Green for recoveries

SELECT * FROM payments_lakehouse.gold.dashboard_cascading_impact;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 8: A/B Test Results Summary

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_ab_test_results AS
WITH test_groups AS (
  SELECT 
    CASE 
      WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 'Control Group (Baseline)'
      ELSE 'Treatment Group (Optimized)'
    END AS test_group,
    COUNT(*) AS sample_size,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS successes,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS success_rate,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS total_approved_volume,
    AVG(amount) AS avg_transaction_amount,
    AVG(risk_score) AS avg_risk_score,
    SUM(CASE WHEN approval_status = 'declined' THEN 1 ELSE 0 END) AS failures,
    -- Processing costs
    SUM(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 0.10 ELSE 0.20 END) AS total_processing_cost,
    AVG(CASE WHEN chosen_solution_stack IN ('Antifraud', 'DataShareOnly') THEN 0.10 ELSE 0.20 END) AS avg_processing_cost
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
  GROUP BY test_group
)
SELECT 
  t1.test_group AS control_group,
  t2.test_group AS treatment_group,
  -- Sample sizes
  t1.sample_size AS control_sample_size,
  t2.sample_size AS treatment_sample_size,
  -- Success rates
  t1.success_rate AS control_success_rate,
  t2.success_rate AS treatment_success_rate,
  ROUND(t2.success_rate - t1.success_rate, 2) AS absolute_lift,
  ROUND((t2.success_rate - t1.success_rate) / t1.success_rate * 100, 2) AS relative_lift_pct,
  -- Statistical significance (simplified Z-test)
  CASE 
    WHEN ABS((t2.success_rate - t1.success_rate) / 
         SQRT((t1.success_rate * (100 - t1.success_rate) / t1.sample_size) + 
              (t2.success_rate * (100 - t2.success_rate) / t2.sample_size))) > 1.96
    THEN 'Statistically Significant (p < 0.05)'
    ELSE 'Not Significant'
  END AS statistical_significance,
  -- Revenue metrics
  t1.total_approved_volume AS control_revenue,
  t2.total_approved_volume AS treatment_revenue,
  t2.total_approved_volume - t1.total_approved_volume AS incremental_revenue,
  -- Cost metrics
  t1.total_processing_cost AS control_cost,
  t2.total_processing_cost AS treatment_cost,
  t2.total_processing_cost - t1.total_processing_cost AS incremental_cost,
  -- ROI
  CASE 
    WHEN (t2.total_processing_cost - t1.total_processing_cost) > 0
    THEN ROUND(((t2.total_approved_volume - t1.total_approved_volume) / 
                (t2.total_processing_cost - t1.total_processing_cost) - 1) * 100, 2)
    ELSE NULL
  END AS roi_pct,
  -- Confidence interval (95%)
  ROUND(t2.success_rate - t1.success_rate - 1.96 * 
        SQRT((t1.success_rate * (100 - t1.success_rate) / t1.sample_size) + 
             (t2.success_rate * (100 - t2.success_rate) / t2.sample_size)), 2) AS ci_lower_bound,
  ROUND(t2.success_rate - t1.success_rate + 1.96 * 
        SQRT((t1.success_rate * (100 - t1.success_rate) / t1.sample_size) + 
             (t2.success_rate * (100 - t2.success_rate) / t2.sample_size)), 2) AS ci_upper_bound,
  -- Recommendation
  CASE 
    WHEN t2.success_rate > t1.success_rate 
         AND ABS((t2.success_rate - t1.success_rate) / 
             SQRT((t1.success_rate * (100 - t1.success_rate) / t1.sample_size) + 
                  (t2.success_rate * (100 - t2.success_rate) / t2.sample_size))) > 1.96
    THEN '✅ RECOMMEND: Deploy optimized routing to 100% of traffic'
    WHEN t2.success_rate > t1.success_rate
    THEN '⚠️ MONITOR: Positive trend but needs more data'
    ELSE '❌ STOP: No significant improvement'
  END AS recommendation
FROM test_groups t1
CROSS JOIN test_groups t2
WHERE t1.test_group = 'Control Group (Baseline)'
  AND t2.test_group = 'Treatment Group (Optimized)';

-- Visualization Type: Comparison Table with visual indicators
-- Show confidence intervals as error bars
-- Color code recommendations

SELECT * FROM payments_lakehouse.gold.dashboard_ab_test_results;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query 9: Summary KPIs - Optimization Impact

-- COMMAND ----------

CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_optimization_kpis AS
WITH baseline AS (
  SELECT 
    COUNT(*) AS txn_count,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
    AND chosen_solution_stack IN ('Antifraud', 'DataShareOnly')
),
optimized AS (
  SELECT 
    COUNT(*) AS txn_count,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS approval_rate,
    SUM(CASE WHEN approval_status = 'approved' THEN amount ELSE 0 END) AS approved_volume
  FROM payments_lakehouse.silver.payments_enriched_stream
  WHERE timestamp >= current_timestamp() - INTERVAL 30 DAYS
    AND chosen_solution_stack NOT IN ('Antifraud', 'DataShareOnly')
)
SELECT 
  -- Approval rate metrics
  b.approval_rate AS baseline_approval_rate,
  o.approval_rate AS optimized_approval_rate,
  ROUND(o.approval_rate - b.approval_rate, 2) AS approval_rate_uplift_pct,
  ROUND((o.approval_rate - b.approval_rate) / b.approval_rate * 100, 2) AS approval_rate_improvement_pct,
  
  -- Volume metrics
  b.approved_volume AS baseline_approved_volume,
  o.approved_volume AS optimized_approved_volume,
  o.approved_volume - b.approved_volume AS incremental_revenue_usd,
  ROUND((o.approved_volume - b.approved_volume) / b.approved_volume * 100, 2) AS revenue_uplift_pct,
  
  -- Projected annual impact
  (o.approved_volume - b.approved_volume) * 12 AS projected_annual_revenue_usd,
  
  -- Transaction counts
  b.txn_count + o.txn_count AS total_transactions_analyzed,
  o.txn_count AS transactions_using_optimization,
  ROUND(o.txn_count * 100.0 / (b.txn_count + o.txn_count), 2) AS optimization_adoption_pct,
  
  -- Success metrics
  'Active' AS optimization_status,
  current_timestamp() AS last_updated,
  
  -- Business impact summary
  CASE 
    WHEN o.approval_rate > b.approval_rate + 2 THEN '🚀 Exceptional Performance'
    WHEN o.approval_rate > b.approval_rate + 1 THEN '✅ Strong Performance'
    WHEN o.approval_rate > b.approval_rate THEN '📈 Positive Impact'
    ELSE '⚠️ Needs Review'
  END AS performance_rating
FROM baseline b
CROSS JOIN optimized o;

-- Visualization Type: Large KPI Cards
-- Display key metrics with delta indicators and trend arrows

SELECT * FROM payments_lakehouse.gold.dashboard_optimization_kpis;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Dashboard Layout Recommendations
-- MAGIC 
-- MAGIC **Page 1: Executive Summary**
-- MAGIC - Top: Large KPI cards (Query 9: Uplift %, revenue gain, adoption %)
-- MAGIC - Center: Comparison bars (Query 1: Before/After side-by-side)
-- MAGIC - Bottom: Time series (Query 4: Approval rate trend with shaded uplift area)
-- MAGIC 
-- MAGIC **Page 2: Detailed Performance**
-- MAGIC - Top: Segmented uplift table (Query 2: By geography, channel, amount)
-- MAGIC - Middle Left: Solution performance scatter (Query 3: Cost vs approval)
-- MAGIC - Middle Right: Geographic uplift lollipop chart (Query 6)
-- MAGIC - Bottom: Revenue impact area chart (Query 5: Daily/cumulative)
-- MAGIC 
-- MAGIC **Page 3: Advanced Analytics**
-- MAGIC - Top: A/B test results table (Query 8: Statistical significance)
-- MAGIC - Middle: Cascading waterfall chart (Query 7: Recovery analysis)
-- MAGIC - Bottom: Solution effectiveness heatmap
-- MAGIC 
-- MAGIC **Interactive Features:**
-- MAGIC - Date range selector (7/14/30/90 days)
-- MAGIC - Segment filters (geography, channel, amount range)
-- MAGIC - Comparison mode toggle (show/hide baseline)
-- MAGIC - Export to PDF/PowerPoint for stakeholder presentations
-- MAGIC 
-- MAGIC **Filters:**
-- MAGIC - Time period (default: last 30 days)
-- MAGIC - Geography (multi-select)
-- MAGIC - Channel (online, mobile, pos)
-- MAGIC - Transaction amount range
-- MAGIC - Merchant category
-- MAGIC - Solution type
-- MAGIC 
-- MAGIC **Refresh Rate:** Every 5 minutes
-- MAGIC 
-- MAGIC **Alert Triggers:**
-- MAGIC - Approval rate uplift drops below 1%
-- MAGIC - Optimization adoption drops below 50%
-- MAGIC - Revenue impact turns negative
-- MAGIC - Statistical significance lost in A/B test
-- MAGIC 
-- MAGIC **Success Metrics to Highlight:**
-- MAGIC - ✅ Approval rate improvement: Target +2-5%
-- MAGIC - ✅ Revenue uplift: Target +$500K-$2M monthly
-- MAGIC - ✅ ROI: Target 10x (revenue gain vs processing cost)
-- MAGIC - ✅ Optimization adoption: Target 80%+
