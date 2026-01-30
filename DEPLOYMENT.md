# Deployment Checklist

## Pre-Deployment

- [ ] **Azure Databricks Workspace**
  - [ ] Premium or Enterprise tier workspace provisioned
  - [ ] Unity Catalog enabled
  - [ ] Compute configured with appropriate instance types
  - [ ] Storage accounts (ADLS Gen2) configured for Delta Lake

- [ ] **Access & Permissions**
  - [ ] Service principal or user credentials with:
    - [ ] CREATE CATALOG, CREATE SCHEMA permissions
    - [ ] READ/WRITE access to storage accounts
    - [ ] MLflow experiment access
    - [ ] Databricks Apps deployment permissions

- [ ] **Configuration Files Uploaded**
  - [ ] `routing_policies.json` → `dbfs:/payments_demo/config/`
  - [ ] `retry_policies.json` → `dbfs:/payments_demo/config/`
  - [ ] `reason_codes.json` → `dbfs:/payments_demo/config/`

## Deployment Steps

### Step 1: Catalog Setup (5 minutes)

- [ ] Execute SQL to create catalog structure:
  ```sql
  CREATE CATALOG IF NOT EXISTS payments_lakehouse;
  CREATE SCHEMA IF NOT EXISTS payments_lakehouse.bronze;
  CREATE SCHEMA IF NOT EXISTS payments_lakehouse.silver;
  CREATE SCHEMA IF NOT EXISTS payments_lakehouse.gold;
  ```

### Step 2: Data Ingestion (10 minutes)

- [ ] Run **Notebook 01: Ingest Synthetic Data**
  - [ ] Wait for streaming ingestion to generate ~5,000-10,000 transactions
  - [ ] Verify Bronze tables created:
    - [ ] `cardholders_dim` (100,000 records)
    - [ ] `merchants_dim` (50,000 records)
    - [ ] `external_risk_signals` (~105 records)
    - [ ] `transactions_raw` (streaming)
  - [ ] Stop streaming query after sufficient data collected

### Step 3: Stream Enrichment & Smart Checkout (10 minutes)

- [ ] Run **Notebook 02: Stream Enrichment & Smart Checkout**
  - [ ] Wait for streaming processing to enrich transactions
  - [ ] Verify Silver table created:
    - [ ] `payments_enriched_stream` with Smart Checkout decisions
  - [ ] Check sample records for:
    - [ ] `recommended_solution_name`
    - [ ] `expected_approval_prob`
    - [ ] `approval_uplift_pct`
  - [ ] Stop streaming query

### Step 4: Reason Code Analytics (5 minutes)

- [ ] Run **Notebook 03: Reason Code Performance**
  - [ ] Verify Gold tables created:
    - [ ] `decline_distribution`
    - [ ] `decline_by_issuer`
    - [ ] `decline_by_geography`
    - [ ] `decline_by_merchant_cluster`
    - [ ] `decline_by_solution_mix`
    - [ ] `decline_by_channel`
    - [ ] `decline_trends`
    - [ ] `reason_code_insights`
    - [ ] `smart_checkout_config_recommendations`
    - [ ] `decline_heatmap_issuer_reason`
  - [ ] Review sample insights for actionability

### Step 5: Smart Retry ML Model (10 minutes)

- [ ] Run **Notebook 04: Smart Retry**
  - [ ] Wait for synthetic retry history generation
  - [ ] Verify model training completes:
    - [ ] MLflow experiment created
    - [ ] Model registered in Model Registry
    - [ ] AUC > 0.75, Accuracy > 0.80
  - [ ] Verify Gold tables created:
    - [ ] `retry_history` (Silver)
    - [ ] `smart_retry_recommendations`
    - [ ] `retry_model_feature_importance`
  - [ ] Check retry recommendation distribution

### Step 6: SQL Dashboards (5 minutes)

- [ ] Run **Notebook 05: Dashboards & Genie Examples**
  - [ ] Verify all views created:
    - [ ] `v_executive_kpis`
    - [ ] `v_approval_trends_hourly`
    - [ ] `v_performance_by_geography`
    - [ ] `v_smart_checkout_solution_performance`
    - [ ] `v_solution_performance_by_geography`
    - [ ] `v_solution_performance_by_issuer`
    - [ ] `v_solution_performance_by_channel`
    - [ ] `v_top_decline_reasons`
    - [ ] `v_actionable_insights_summary`
    - [ ] `v_decline_trends_analysis`
    - [ ] `v_retry_recommendation_summary`
    - [ ] `v_retry_by_reason_code`
    - [ ] `v_retry_value_recovery`
    - [ ] And more...
  - [ ] Query sample views to verify data

### Step 7: Databricks App (Optional, 10 minutes)

- [ ] Open **Notebook 06: App Demo UI**
- [ ] Deploy as Databricks App:
  - [ ] Click "Deploy" → "Create App"
  - [ ] Configure app name: "Payment Authorization Command Center"
  - [ ] Set compute: Use existing cluster or serverless
  - [ ] Deploy and wait for app to start
- [ ] Access app URL and verify:
  - [ ] KPI tiles display correctly
  - [ ] Live transaction feed loads
  - [ ] Charts and visualizations render
  - [ ] Interactive controls work (sliders, filters)

## Post-Deployment Validation

### Data Quality Checks

- [ ] **Bronze Layer**
  - [ ] Row counts match expectations
  - [ ] No null values in key fields
  - [ ] Timestamp ranges are correct

- [ ] **Silver Layer**
  - [ ] All transactions have Smart Checkout decisions
  - [ ] `expected_approval_prob` between 0 and 1
  - [ ] `approval_uplift_pct` calculated correctly

- [ ] **Gold Layer**
  - [ ] Aggregations sum to 100% where expected
  - [ ] No duplicate insights or recommendations
  - [ ] All reason codes have taxonomy mapping

### Performance Checks

- [ ] Streaming latency < 10 seconds
- [ ] Query performance on Gold views < 5 seconds
- [ ] ML model inference < 1 second per transaction
- [ ] Dashboard refresh < 10 seconds

### Functional Checks

- [ ] **Smart Checkout**
  - [ ] Selects different solutions for different risk profiles
  - [ ] Mandatory 3DS applied in EU geography
  - [ ] Cascading path generated for all transactions

- [ ] **Reason Code Analytics**
  - [ ] Insights generated for top decline codes
  - [ ] Recommended actions populated
  - [ ] Heatmap data complete

- [ ] **Smart Retry**
  - [ ] Retry actions distributed (RETRY_NOW, RETRY_LATER, DO_NOT_RETRY)
  - [ ] Success probabilities reasonable (0.3-0.8)
  - [ ] Suggested delays vary by reason code

## Demo Preparation

- [ ] **Executive Demo (15 minutes)**
  - [ ] Start with Executive KPI dashboard
  - [ ] Show approval rate improvement trend
  - [ ] Highlight geographic performance
  - [ ] Display Smart Retry value recovery

- [ ] **Technical Demo (30 minutes)**
  - [ ] Walk through Bronze → Silver → Gold flow
  - [ ] Show Smart Checkout decision logic
  - [ ] Explain ML model training and feature importance
  - [ ] Demonstrate streaming architecture

- [ ] **Interactive Demo (20 minutes)**
  - [ ] Use Databricks App Command Center
  - [ ] Filter live transaction feed
  - [ ] Adjust policy thresholds (What-If analysis)
  - [ ] Show Sankey flow visualization

## Troubleshooting

### Common Issues

1. **Streaming query fails**
   - Check checkpoint location permissions
   - Verify source table exists
   - Review error logs in Spark UI

2. **ML model training slow**
   - Increase cluster size or use GPU
   - Reduce training data sample size
   - Adjust hyperparameters (maxIter, maxDepth)

3. **Databricks App won't deploy**
   - Verify Streamlit library installed
   - Check app code for syntax errors
   - Ensure compute has sufficient memory

4. **Views return no data**
   - Verify underlying tables populated
   - Check timestamp filters (time zone issues)
   - Review join conditions

## Rollback Plan

If deployment fails:

1. **Drop catalog**: `DROP CATALOG IF EXISTS payments_lakehouse CASCADE;`
2. **Delete checkpoint files**: `dbfs rm -r dbfs:/payments_demo/checkpoints/`
3. **Delete MLflow experiments**: From MLflow UI
4. **Undeploy Databricks App**: From Apps UI

## Success Criteria

- [ ] All 8 notebooks executed successfully
- [ ] 40+ Gold tables/views created
- [ ] ML model AUC > 0.75
- [ ] Databricks App deployed and accessible
- [ ] Demo walkthrough completed with stakeholders

---

**Deployment completed by**: _________________  
**Date**: _________________  
**Notes**: _________________
