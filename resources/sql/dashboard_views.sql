-- Example SQL views for Databricks SQL dashboards

USE CATALOG payments_lakehouse;
USE SCHEMA gold;

-- View: Real-time KPI snapshot for executive dashboard
CREATE OR REPLACE VIEW v_realtime_kpi_snapshot AS
SELECT 
    CURRENT_TIMESTAMP() as snapshot_time,
    COUNT(*) as total_transactions_24h,
    ROUND(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct,
    ROUND(AVG(approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(composite_risk_score), 3) as avg_risk_score,
    ROUND(SUM(amount), 2) as total_value_usd,
    ROUND(SUM(CASE WHEN is_approved THEN amount ELSE 0 END), 2) as approved_value_usd,
    ROUND(SUM(CASE WHEN NOT is_approved THEN amount ELSE 0 END), 2) as declined_value_usd
FROM payments_lakehouse.silver.payments_enriched_stream
WHERE timestamp >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS;

-- View: Comparison of current performance vs historical baseline
CREATE OR REPLACE VIEW v_performance_vs_baseline AS
WITH current_metrics AS (
    SELECT 
        ROUND(AVG(CASE WHEN is_approved THEN 1 ELSE 0 END) * 100, 2) as current_approval_rate,
        ROUND(AVG(composite_risk_score), 3) as current_risk_score,
        ROUND(AVG(solution_cost), 2) as current_avg_cost
    FROM payments_lakehouse.silver.payments_enriched_stream
    WHERE timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
),
baseline_metrics AS (
    SELECT 
        85.0 as baseline_approval_rate,
        0.45 as baseline_risk_score,
        0.15 as baseline_avg_cost
)
SELECT 
    c.current_approval_rate,
    b.baseline_approval_rate,
    ROUND(c.current_approval_rate - b.baseline_approval_rate, 2) as approval_improvement_pct,
    c.current_risk_score,
    b.baseline_risk_score,
    ROUND((b.baseline_risk_score - c.current_risk_score) * 100, 2) as risk_reduction_pct,
    c.current_avg_cost,
    b.baseline_avg_cost,
    ROUND(c.current_avg_cost - b.baseline_avg_cost, 2) as cost_delta_usd
FROM current_metrics c, baseline_metrics b;

-- View: Top performing solution mixes
CREATE OR REPLACE VIEW v_top_solution_mixes AS
SELECT 
    recommended_solution_name,
    COUNT(*) as txn_count,
    ROUND(AVG(CASE WHEN is_approved THEN 1 ELSE 0 END) * 100, 2) as approval_rate_pct,
    ROUND(AVG(approval_uplift_pct), 2) as avg_uplift_pct,
    ROUND(AVG(adjusted_risk_score), 3) as avg_risk_score,
    ROUND(AVG(solution_cost), 2) as avg_cost_usd,
    -- ROI calculation: (uplift * avg_amount - cost) / cost
    ROUND((AVG(approval_uplift_pct) * AVG(amount) / 100 - AVG(solution_cost)) / NULLIF(AVG(solution_cost), 0), 2) as roi_ratio
FROM payments_lakehouse.silver.payments_enriched_stream
WHERE timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY recommended_solution_name
HAVING COUNT(*) > 100
ORDER BY roi_ratio DESC;

-- View: Decline recovery opportunities
CREATE OR REPLACE VIEW v_decline_recovery_opportunities AS
SELECT 
    txn.reason_code,
    rc.description,
    COUNT(*) as decline_count,
    ROUND(AVG(amount), 2) as avg_amount_usd,
    ROUND(SUM(amount), 2) as total_declined_value_usd,
    -- Estimated recoverable based on reason code type
    CASE 
        WHEN txn.reason_code IN ('51_INSUFFICIENT_FUNDS', '91_ISSUER_UNAVAILABLE') THEN 'High (50-70%)'
        WHEN txn.reason_code IN ('05_DO_NOT_HONOR', '61_EXCEEDS_LIMIT', '65_EXCEEDS_FREQUENCY') THEN 'Medium (30-50%)'
        WHEN txn.reason_code IN ('63_SECURITY_VIOLATION', '57_FUNCTION_NOT_PERMITTED') THEN 'Low (10-30%)'
        ELSE 'Very Low (<10%)'
    END as recovery_potential,
    rc.is_actionable,
    ARRAY_JOIN(rc.recommended_actions, ' | ') as recommended_actions
FROM payments_lakehouse.silver.payments_enriched_stream txn
JOIN payments_lakehouse.bronze.reason_code_dim rc ON txn.reason_code = rc.reason_code
WHERE NOT txn.is_approved
    AND txn.timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY txn.reason_code, rc.description, rc.is_actionable, rc.recommended_actions
ORDER BY decline_count DESC;
