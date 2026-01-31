-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 05 - Dashboards, SQL Analytics & Genie Examples
-- MAGIC
-- MAGIC ## Overview
-- MAGIC This notebook creates:
-- MAGIC - **Executive KPI Dashboard**: High-level approval rates, uplift, and trends
-- MAGIC - **Smart Checkout Performance**: Solution mix effectiveness
-- MAGIC - **Reason Code Analytics**: Decline analysis and remediation tracking
-- MAGIC - **Smart Retry Dashboard**: Retry recommendations and recovery rates
-- MAGIC - **Genie Examples**: Natural language queries for business users
-- MAGIC
-- MAGIC ## Target Audience
-- MAGIC - Executives: KPI monitoring and strategic insights
-- MAGIC - Product Managers: Feature performance and optimization opportunities
-- MAGIC - Risk/Fraud Teams: Risk metrics and compliance monitoring
-- MAGIC - Data Analysts: Deep-dive analytics and root cause analysis

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Setup

-- COMMAND ----------

USE CATALOG payments_lakehouse;
USE SCHEMA gold;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 1. Executive KPI Dashboard Views

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Overall Performance Metrics

-- COMMAND ----------

-- DBTITLE 1,Overall Performance Metrics
-- Create a view for transaction approval performance and Smart Checkout impact
CREATE OR REPLACE VIEW transaction_approval_performance_smart_checkout
AS
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT t.cardholder_id) AS unique_cardholders,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) AS avg_approval_uplift_pct,
    ROUND(AVG(t.expected_approval_prob) * 100, 2) AS avg_expected_approval_pct,
    ROUND(AVG(t.adjusted_risk_score), 3) AS avg_adjusted_risk_score,
    ROUND(AVG(t.solution_cost), 2) AS avg_solution_cost_usd
FROM payments_lakehouse.silver.payments_enriched_stream t ;

SELECT * FROM transaction_approval_performance_smart_checkout;

-- COMMAND ----------

-- DBTITLE 1,Cell 7
-- Create a view for transaction approval performance by reason code
CREATE OR REPLACE VIEW transaction_approval_performance_smart_reason_code
AS
SELECT
    t.reason_code,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT t.cardholder_id) AS unique_cardholders,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) AS avg_approval_uplift_pct,
    ROUND(AVG(t.expected_approval_prob) * 100, 2) AS avg_expected_approval_pct,
    ROUND(AVG(t.adjusted_risk_score), 3) AS avg_adjusted_risk_score,
    ROUND(SUM(t.amount), 2) AS total_transaction_value
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.reason_code
ORDER BY total_transactions DESC;

SELECT * FROM transaction_approval_performance_smart_reason_code;

-- COMMAND ----------

-- DBTITLE 1,Cell 8
-- Create a view for Smart Retry performance metrics
CREATE OR REPLACE VIEW transaction_approval_performance_smart_retry
AS
SELECT
    COUNT(*) AS total_declined_transactions,
    COUNT(DISTINCT t.transaction_id) AS unique_transactions,
    ROUND(AVG(retry_success_probability) * 100, 2) AS avg_retry_success_prob_pct,
    ROUND(SUM(CASE WHEN retry_action = 'RETRY_NOW' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS immediate_retry_pct,
    ROUND(SUM(CASE WHEN retry_action = 'RETRY_LATER' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS delayed_retry_pct,
    ROUND(SUM(CASE WHEN retry_action = 'DO_NOT_RETRY' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_retry_pct,
    ROUND(AVG(suggested_delay_hours), 2) AS avg_suggested_delay_hours,
    ROUND(AVG(expected_approval_change_pct), 2) AS avg_expected_approval_change_pct,
    ROUND(AVG(t.composite_risk_score), 3) AS avg_composite_risk_score
FROM payments_lakehouse.gold.smart_retry_recommendations;

SELECT * FROM transaction_approval_performance_smart_retry;

-- COMMAND ----------

-- Create view for executive KPIs
CREATE OR REPLACE VIEW v_executive_kpis AS
SELECT 
    -- Transaction volumes
    COUNT(*) as total_transactions,
    COUNT(DISTINCT t.cardholder_id) as unique_cardholders,
    COUNT(DISTINCT t.merchant_id) as unique_merchants,
    
    -- Approval metrics
    SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN NOT t.is_approved THEN 1 ELSE 0 END) as declined_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    
    -- Smart Checkout uplift
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_approval_uplift_pct,
    
    -- Risk metrics
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score,
    ROUND(AVG(t.adjusted_risk_score), 3) as avg_adjusted_risk_score,
    ROUND((AVG(t.composite_risk_score) - AVG(t.adjusted_risk_score)) * 100, 2) as risk_reduction_pct,
    
    -- Financial metrics
    ROUND(SUM(t.amount), 2) as total_transaction_value,
    ROUND(SUM(CASE WHEN t.is_approved THEN t.amount ELSE 0 END), 2) as approved_value,
    ROUND(SUM(CASE WHEN NOT t.is_approved THEN t.amount ELSE 0 END), 2) as declined_value,
    ROUND(AVG(t.solution_cost), 2) as avg_solution_cost,
    
    -- Time period
    MIN(t.timestamp) as period_start,
    MAX(t.timestamp) as period_end
FROM payments_lakehouse.silver.payments_enriched_stream t ;

-- Query the view
SELECT * FROM v_executive_kpis;

-- COMMAND ----------

COMMENT ON VIEW v_executive_kpis IS 'Executive KPI summary including approval rates, uplift, risk metrics, and financial performance';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Approval Rate Trends Over Time

-- COMMAND ----------

CREATE OR REPLACE VIEW v_approval_trends_hourly AS
SELECT 
    DATE_TRUNC('hour', t.timestamp) as hour,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score,
    ROUND(SUM(t.amount), 2) as total_value
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY DATE_TRUNC('hour', t.timestamp)
ORDER BY hour DESC;

SELECT * FROM v_approval_trends_hourly LIMIT 48;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Geographic Performance

-- COMMAND ----------

CREATE OR REPLACE VIEW v_performance_by_geography AS
SELECT 
    cardholder_country as geography,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score,
    ROUND(AVG(t.country_risk_score), 3) as avg_country_risk,
    ROUND(SUM(t.amount), 2) as total_transaction_value,
    COUNT(DISTINCT t.merchant_id) as unique_merchants,
    COUNT(DISTINCT t.cardholder_id) as unique_cardholders
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.cardholder_country
ORDER BY transaction_count DESC;

SELECT * FROM v_performance_by_geography LIMIT 20;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 2. Smart Checkout Performance Dashboard

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Solution Mix Effectiveness

-- COMMAND ----------

CREATE OR REPLACE VIEW v_smart_checkout_solution_performance AS
SELECT 
    recommended_solution_name as solution_mix,
    COUNT(*) as transaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total,
    ROUND(AVG(t.expected_approval_prob) * 100, 2) as avg_expected_approval_pct,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as actual_approval_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.adjusted_risk_score), 3) as avg_risk_score,
    ROUND(AVG(t.solution_cost), 2) as avg_cost_usd,
    ROUND(SUM(t.amount), 2) as total_transaction_value
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.recommended_solution_name
ORDER BY transaction_count DESC;

SELECT * FROM v_smart_checkout_solution_performance;

-- COMMAND ----------

COMMENT ON VIEW v_smart_checkout_solution_performance IS 'Performance metrics for each payment solution mix including approval rates, uplift, and costs';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Solution Performance by Geography

-- COMMAND ----------

CREATE OR REPLACE VIEW v_solution_performance_by_geography AS
SELECT 
    cardholder_country as geography,
    recommended_solution_name as solution_mix,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.solution_cost), 2) as avg_cost_usd
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.cardholder_country, t.recommended_solution_name
HAVING COUNT(*) > 10
ORDER BY geography, transaction_count DESC;

SELECT * FROM v_solution_performance_by_geography LIMIT 50;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Solution Performance by Issuer

-- COMMAND ----------

CREATE OR REPLACE VIEW v_solution_performance_by_issuer AS
SELECT 
    card_network as issuer,
    recommended_solution_name as solution_mix,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.card_network, t.recommended_solution_name
ORDER BY issuer, transaction_count DESC;

SELECT * FROM v_solution_performance_by_issuer;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Solution Performance by t.Channel

-- COMMAND ----------

CREATE OR REPLACE VIEW v_solution_performance_by_channel AS
SELECT 
    t.channel,
    recommended_solution_name as solution_mix,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.amount), 2) as avg_amount
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.channel, t.recommended_solution_name
ORDER BY t.channel, transaction_count DESC;

SELECT * FROM v_solution_performance_by_channel;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 3. Reason Code Analytics Dashboard

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Top Decline Reasons

-- COMMAND ----------

CREATE OR REPLACE VIEW v_top_decline_reasons AS
SELECT 
    d.reason_code,
    rc.category,
    rc.severity,
    rc.description,
    d.decline_count,
    d.pct_of_declines,
    d.avg_risk_score,
    d.avg_amount,
    rc.is_actionable
FROM payments_lakehouse.gold.decline_distribution d
JOIN payments_lakehouse.bronze.reason_code_dim rc ON d.reason_code = rc.reason_code
ORDER BY d.decline_count DESC;

SELECT * FROM v_top_decline_reasons LIMIT 15;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Actionable Insights Summary

-- COMMAND ----------

CREATE OR REPLACE VIEW v_actionable_insights_summary AS
SELECT 
    insight_id,
    segment,
    issue,
    priority,
    estimated_impact,
    ARRAY_JOIN(root_causes, ' | ') as root_causes_summary,
    ARRAY_JOIN(recommended_actions, ' | ') as recommended_actions_summary
FROM payments_lakehouse.gold.reason_code_insights
ORDER BY 
    CASE priority 
        WHEN 'High' THEN 1 
        WHEN 'Medium' THEN 2 
        ELSE 3 
    END,
    insight_id;

SELECT * FROM v_actionable_insights_summary;

-- COMMAND ----------

COMMENT ON VIEW v_actionable_insights_summary IS 'Prioritized actionable insights with root causes and recommended remediation actions';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Decline Heatmap: Issuer vs Reason Code

-- COMMAND ----------

-- Query heatmap data
SELECT * FROM payments_lakehouse.gold.decline_heatmap_issuer_reason;

-- COMMAND ----------

-- DBTITLE 1,Create Dashboard SQL Queries
-- MAGIC %md
-- MAGIC ### Decline Trends Analysis

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Approval Trend
CREATE OR REPLACE VIEW v_decline_trends_analysis AS
SELECT 
    hour,
    t.reason_code,
    decline_count,
    avg_risk_score,
    SUM(decline_count) OVER (PARTITION BY t.reason_code ORDER BY hour ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7hr_count,
    AVG(decline_count) OVER (PARTITION BY t.reason_code ORDER BY hour ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) as rolling_24hr_avg
FROM payments_lakehouse.gold.decline_trends
ORDER BY hour DESC, decline_count DESC;

SELECT * FROM v_decline_trends_analysis LIMIT 100;

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Solution Performance
-- MAGIC %md
-- MAGIC ## 4. Smart Retry Dashboard

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Geographic Heatmap
-- MAGIC %md
-- MAGIC ### Retry Recommendation Summary

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Top Declines
CREATE OR REPLACE VIEW v_retry_recommendation_summary AS
SELECT 
    retry_action,
    COUNT(*) as recommendation_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total,
    ROUND(AVG(retry_success_probability) * 100, 2) as avg_success_prob_pct,
    ROUND(AVG(suggested_delay_hours), 1) as avg_suggested_delay_hours,
    ROUND(AVG(expected_approval_change_pct), 2) as avg_expected_uplift_pct
FROM payments_lakehouse.gold.smart_retry_recommendations
GROUP BY retry_action
ORDER BY recommendation_count DESC;

SELECT * FROM v_retry_recommendation_summary;

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Retry Distribution
COMMENT ON VIEW v_retry_recommendation_summary IS 'Summary of Smart Retry recommendations by action type with success probabilities';

-- COMMAND ----------

-- DBTITLE 1,Dashboard Query: Revenue Recovery
-- MAGIC %md
-- MAGIC ### Retry Recommendations by Reason Code

-- COMMAND ----------

CREATE OR REPLACE VIEW v_retry_by_reason_code AS
SELECT 
    r.reason_code,
    rc.description,
    rc.category,
    r.retry_action,
    COUNT(*) as recommendation_count,
    ROUND(AVG(r.retry_success_probability) * 100, 2) as avg_success_prob_pct,
    ROUND(AVG(r.suggested_delay_hours), 1) as avg_delay_hours
FROM payments_lakehouse.gold.smart_retry_recommendations r
JOIN payments_lakehouse.bronze.reason_code_dim rc ON r.reason_code = rc.reason_code
GROUP BY r.reason_code, rc.description, rc.category, r.retry_action
ORDER BY r.reason_code, recommendation_count DESC;

SELECT * FROM v_retry_by_reason_code;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Retry Value Recovery Estimate

-- COMMAND ----------

-- DBTITLE 1,Create Genie-Optimized Views
CREATE OR REPLACE VIEW v_retry_value_recovery AS
SELECT 
    rec.retry_action,
    COUNT(*) as transaction_count,
    ROUND(SUM(txn.amount), 2) as total_declined_value,
    ROUND(SUM(rec.retry_success_probability * txn.amount), 2) as estimated_recoverable_value,
    ROUND(SUM(rec.retry_success_probability * txn.amount) * 100.0 / SUM(txn.amount), 2) as recovery_rate_pct
FROM payments_lakehouse.gold.smart_retry_recommendations rec
JOIN payments_lakehouse.silver.payments_enriched_stream txn 
    ON rec.transaction_id = txn.transaction_id
WHERE NOT txn.is_approved
GROUP BY rec.retry_action
ORDER BY estimated_recoverable_value DESC;

SELECT * FROM v_retry_value_recovery;

-- COMMAND ----------

-- DBTITLE 1,Genie View: Solution Summary
COMMENT ON VIEW v_retry_value_recovery IS 'Estimated financial value recovery from Smart Retry recommendations';

-- COMMAND ----------

-- DBTITLE 1,Genie View: Decline Summary
-- MAGIC %md
-- MAGIC ### Retry Model Feature Importance

-- COMMAND ----------

-- DBTITLE 1,Genie View: Retry Summary
SELECT 
    feature,
    ROUND(importance, 4) as importance_score,
    ROUND(importance * 100, 2) as importance_pct
FROM payments_lakehouse.gold.retry_model_feature_importance
ORDER BY importance DESC
LIMIT 15;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Approval Funnel Analysis

-- COMMAND ----------

CREATE OR REPLACE VIEW v_approval_funnel AS
SELECT 
    'Total Transactions' as stage,
    1 as stage_order,
    COUNT(*) as transaction_count,
    100.0 as pct_of_initial
FROM payments_lakehouse.silver.payments_enriched_stream t UNION ALL

SELECT 
    'After Smart Checkout' as stage,
    2 as stage_order,
    COUNT(*) as transaction_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments_lakehouse.silver.payments_enriched_stream), 2) as pct_of_initial
FROM payments_lakehouse.silver.payments_enriched_stream t UNION ALL

SELECT 
    'Approved' as stage,
    3 as stage_order,
    SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / (SELECT COUNT(*) FROM payments_lakehouse.silver.payments_enriched_stream), 2) as pct_of_initial
FROM payments_lakehouse.silver.payments_enriched_stream t UNION ALL

SELECT 
    'Declined (Retry Candidates)' as stage,
    4 as stage_order,
    COUNT(*) as transaction_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments_lakehouse.silver.payments_enriched_stream), 2) as pct_of_initial
FROM payments_lakehouse.gold.smart_retry_recommendations
WHERE retry_action != 'DO_NOT_RETRY'

ORDER BY stage_order;

SELECT * FROM v_approval_funnel;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Risk vs Approval Performance Matrix

-- COMMAND ----------

CREATE OR REPLACE VIEW v_risk_approval_matrix AS
SELECT 
    CASE 
        WHEN t.composite_risk_score < 0.3 THEN 'Low Risk (0-0.3)'
        WHEN t.composite_risk_score < 0.6 THEN 'Medium Risk (0.3-0.6)'
        WHEN t.composite_risk_score < 0.85 THEN 'High Risk (0.6-0.85)'
        ELSE 'Critical Risk (0.85+)'
    END as risk_segment,
    COUNT(*) as transaction_count,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.solution_cost), 2) as avg_solution_cost,
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score,
    ROUND(AVG(t.adjusted_risk_score), 3) as avg_adjusted_risk
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY 
    CASE 
        WHEN t.composite_risk_score < 0.3 THEN 'Low Risk (0-0.3)'
        WHEN t.composite_risk_score < 0.6 THEN 'Medium Risk (0.3-0.6)'
        WHEN t.composite_risk_score < 0.85 THEN 'High Risk (0.6-0.85)'
        ELSE 'Critical Risk (0.85+)'
    END
ORDER BY avg_risk_score;

SELECT * FROM v_risk_approval_matrix;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Merchant Segment Performance

-- COMMAND ----------

CREATE OR REPLACE VIEW v_merchant_segment_performance AS
SELECT 
    t.merchant_cluster,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT t.merchant_id) as unique_merchants,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(t.merchant_risk_score), 3) as avg_merchant_risk,
    ROUND(SUM(t.amount), 2) as total_transaction_value
FROM payments_lakehouse.silver.payments_enriched_stream t GROUP BY t.merchant_cluster
ORDER BY t.merchant_cluster;

SELECT * FROM v_merchant_segment_performance;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 6. Genie Examples & Natural Language Queries
-- MAGIC
-- MAGIC Below are example queries that business users can ask using Databricks Genie.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Genie Query Examples
-- MAGIC
-- MAGIC **For Executives:**
-- MAGIC 1. "What is our overall approval rate this week?"
-- MAGIC 2. "Show me approval rate trends by geography"
-- MAGIC 3. "What's the estimated value we're recovering through Smart Retry?"
-- MAGIC 4. "Which payment solution mix has the highest approval rate?"
-- MAGIC
-- MAGIC **For Product Managers:**
-- MAGIC 1. "Which solution combinations are most cost-effective?"
-- MAGIC 2. "How does Smart Checkout performance vary by t.channel?"
-- MAGIC 3. "What's the average approval uplift from using NetworkToken?"
-- MAGIC 4. "Show me the top 5 merchants by transaction volume and their approval rates"
-- MAGIC
-- MAGIC **For Risk/Fraud Teams:**
-- MAGIC 1. "What are the most common security violation decline codes?"
-- MAGIC 2. "Show me high-risk transactions that were approved and their solution mix"
-- MAGIC 3. "Which geographies have the highest fraud risk scores?"
-- MAGIC 4. "How effective is 3DS at reducing risk scores?"
-- MAGIC
-- MAGIC **For Data Analysts:**
-- MAGIC 1. "Explain the main drivers of decline rate increase in LATAM ecommerce last week"
-- MAGIC 2. "For merchant cluster high_risk, which mix of payment solutions increased approval rates the most?"
-- MAGIC 3. "What's the correlation between risk score and approval rate by issuer?"
-- MAGIC 4. "Show me the breakdown of soft vs hard declines by reason code"

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Create Genie-Friendly Views

-- COMMAND ----------

-- Simple view for Genie: Current performance snapshot
CREATE OR REPLACE VIEW v_genie_current_performance AS
SELECT 
    'Overall' as segment,
    COUNT(*) as total_transactions,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_from_smart_checkout_pct,
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score,
    ROUND(SUM(t.amount), 2) as total_value_usd
FROM payments_lakehouse.silver.payments_enriched_stream t ;

SELECT * FROM v_genie_current_performance;

-- COMMAND ----------

-- Simple view for Genie: Decline insights
CREATE OR REPLACE VIEW v_genie_decline_insights AS
SELECT 
    t.reason_code,
    description as reason_description,
    category as decline_category,
    severity,
    CASE WHEN is_actionable THEN 'Yes' ELSE 'No' END as can_be_fixed,
    ARRAY_JOIN(recommended_actions, '; ') as recommended_actions
FROM payments_lakehouse.bronze.reason_code_dim
WHERE is_actionable = true
ORDER BY severity DESC, t.reason_code;

SELECT * FROM v_genie_decline_insights;

-- COMMAND ----------

-- Simple view for Genie: Solution recommendations
CREATE OR REPLACE VIEW v_genie_solution_recommendations AS
SELECT 
    solution_mix,
    transaction_count,
    actual_approval_pct as approval_rate_pct,
    avg_uplift_pct as uplift_vs_baseline_pct,
    avg_cost_usd as cost_per_transaction_usd,
    CASE 
        WHEN avg_uplift_pct > 5 AND avg_cost_usd < 0.20 THEN 'Highly Recommended'
        WHEN avg_uplift_pct > 2 THEN 'Recommended'
        ELSE 'Conditional'
    END as recommendation
FROM v_smart_checkout_solution_performance
WHERE transaction_count > 50
ORDER BY avg_uplift_pct DESC;

SELECT * FROM v_genie_solution_recommendations;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 7. Real-Time Monitoring Queries

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Last Hour Performance

-- COMMAND ----------

CREATE OR REPLACE VIEW v_last_hour_performance AS
SELECT 
    COUNT(*) as transactions_last_hour,
    ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(t.approval_uplift_pct), 2) as avg_uplift_pct,
    COUNT(DISTINCT t.cardholder_id) as unique_cardholders,
    COUNT(DISTINCT t.merchant_id) as unique_merchants,
    ROUND(SUM(t.amount), 2) as total_value_usd,
    ROUND(AVG(t.composite_risk_score), 3) as avg_risk_score
FROM payments_lakehouse.silver.payments_enriched_stream t WHERE t.timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR;

SELECT * FROM v_last_hour_performance;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Active Alerts

-- COMMAND ----------

CREATE OR REPLACE VIEW v_active_alerts AS
-- Alert 1: Approval rate drop
SELECT 
    'Approval Rate Drop' as alert_type,
    'High' as severity,
    CONCAT('Approval rate in last hour: ', 
           CAST(ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS STRING),
           '%') as alert_message,
    CURRENT_TIMESTAMP() as alert_timestamp
FROM payments_lakehouse.silver.payments_enriched_stream t WHERE t.timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
HAVING ROUND(SUM(CASE WHEN t.is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) < 75

UNION ALL

-- Alert 2: High decline volume for specific reason code
SELECT 
    'High Decline Volume' as alert_type,
    'Medium' as severity,
    CONCAT('Elevated ', t.reason_code, ' declines: ', CAST(COUNT(*) AS STRING), ' in last hour') as alert_message,
    CURRENT_TIMESTAMP() as alert_timestamp
FROM payments_lakehouse.silver.payments_enriched_stream t WHERE t.timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
    AND NOT t.is_approved
GROUP BY t.reason_code
HAVING COUNT(*) > 100

UNION ALL

-- Alert 3: High risk transactions
SELECT 
    'High Risk Volume' as alert_type,
    'Critical' as severity,
    CONCAT('High risk transactions: ', CAST(COUNT(*) AS STRING), ' with avg risk ', 
           CAST(ROUND(AVG(t.composite_risk_score), 3) AS STRING)) as alert_message,
    CURRENT_TIMESTAMP() as alert_timestamp
FROM payments_lakehouse.silver.payments_enriched_stream t WHERE t.timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
    AND t.composite_risk_score > 0.75
HAVING COUNT(*) > 50;

SELECT * FROM v_active_alerts;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Summary
-- MAGIC
-- MAGIC ✅ **Dashboard Views Created**:
-- MAGIC - Executive KPI dashboard (9 views)
-- MAGIC - Smart Checkout performance analytics (4 views)
-- MAGIC - Reason Code analytics (5 views)
-- MAGIC - Smart Retry dashboard (3 views)
-- MAGIC - Cross-functional analytics (4 views)
-- MAGIC - Real-time monitoring (2 views)
-- MAGIC
-- MAGIC ✅ **Genie Integration**:
-- MAGIC - Natural language query examples for all stakeholder personas
-- MAGIC - Simplified views optimized for Genie queries
-- MAGIC - Business-friendly field names and descriptions
-- MAGIC
-- MAGIC **Key Dashboards**:
-- MAGIC 1. **Executive Dashboard**: Approval rates, uplift, risk metrics, financial impact
-- MAGIC 2. **Smart Checkout Dashboard**: Solution mix performance, geographic breakdown
-- MAGIC 3. **Reason Code Dashboard**: Decline analysis, actionable insights, heatmaps
-- MAGIC 4. **Smart Retry Dashboard**: Recommendations, value recovery, model performance
-- MAGIC 5. **Real-Time Monitoring**: Last hour metrics, active alerts
-- MAGIC
-- MAGIC **Usage**:
-- MAGIC - All views are queryable via Databricks SQL
-- MAGIC - Can be used to build visual dashboards in Databricks SQL Analytics
-- MAGIC - Compatible with Genie for natural language queries
-- MAGIC - Support real-time monitoring and alerting
-- MAGIC
-- MAGIC **Next Steps**:
-- MAGIC - Notebook 06: Databricks App UI for interactive live monitoring
