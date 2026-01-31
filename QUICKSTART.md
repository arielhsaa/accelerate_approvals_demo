# Quick Start Guide

## 🚀 Get Started in 30 Minutes

This quick start guide will get you up and running with the Payment Authorization demo on Azure Databricks.

---

## Prerequisites

- ✅ Azure Databricks workspace (Premium or Enterprise tier)
- ✅ Unity Catalog enabled
- ✅ Cluster with Databricks Runtime 14.3 LTS+
- ✅ Permissions: CREATE CATALOG, CREATE SCHEMA, CREATE TABLE

---

## Step 1: Upload Files (5 minutes)

### A. Upload Notebooks

In your Databricks workspace, create a folder:

```
/Workspace/Users/<your-email>/accelerate_approvals_demo/
```

Upload all notebooks from the `notebooks/` folder:
- `00_deployment_setup.py` ⭐ (Run this first for automated setup!)
- `01_ingest_synthetic_data.py`
- `02_stream_enrichment_smart_checkout.py`
- `03_reason_code_performance.py`
- `04_smart_retry.py`
- `05_dashboards_and_genie_examples.sql`
- `06_demo_app/06_app_demo_ui.py` (Standard app)
- `07_advanced_app/07_advanced_app_ui.py` (Advanced app - RECOMMENDED)

### B. Upload Configuration Files

**Option A: Automated (Recommended)**
Run `00_deployment_setup` notebook - it handles everything automatically!

**Option B: Manual**
Upload configuration files to DBFS:

```python
# Run this in a Databricks notebook cell
dbutils.fs.mkdirs("dbfs:/payments_demo/config/")

# Then upload the 4 JSON files from resources/config/ to:
# dbfs:/payments_demo/config/routing_policies.json
# dbfs:/payments_demo/config/retry_policies.json
# dbfs:/payments_demo/config/reason_codes.json
# dbfs:/payments_demo/config/policies.json
```

Or use the Databricks UI: Data → DBFS → Upload files

---

## Step 2: Create Catalog (2 minutes)

**Option A: Automated (Recommended)**
Run the `00_deployment_setup` notebook - it creates everything automatically!

**Option B: Manual**
Run this SQL in a notebook or SQL editor:

```sql
CREATE CATALOG IF NOT EXISTS payments_lakehouse;
USE CATALOG payments_lakehouse;

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

COMMENT ON CATALOG payments_lakehouse IS 
'Payment authorization demo: Smart Checkout, Reason Code Analytics, Smart Retry';
```

---

## Step 3: Run Notebooks (15 minutes)

Execute notebooks **in order**. Attach each notebook to your cluster before running.

### Notebook 00: Deployment Setup (2 min) - OPTIONAL BUT RECOMMENDED
- Click "Run All"
- Automatically creates catalog, schemas, uploads configs
- Validates environment and provides recommendations
- ✅ Verify: Catalog and schemas created, configs uploaded

### Notebook 01: Ingest Synthetic Data (3 min)
- Click "Run All"
- Wait for streaming to generate ~5,000-10,000 transactions (1-2 minutes)
- **Stop the streaming query** (scroll to bottom, click Stop)
- ✅ Verify: `cardholders_dim`, `merchants_dim`, `external_risk_signals`, `transactions_raw` tables created

### Notebook 02: Stream Enrichment & Smart Checkout (3 min)
- Click "Run All"
- Wait for streaming to process transactions (1-2 minutes)
- **Stop the streaming query**
- ✅ Verify: `payments_enriched_stream` table created with `recommended_solution_name` column

### Notebook 03: Reason Code Performance (2 min)
- Click "Run All"
- This is a batch notebook, no streaming
- ✅ Verify: Multiple Gold tables created (`decline_distribution`, `reason_code_insights`, etc.)

### Notebook 04: Smart Retry (4 min)
- Click "Run All"
- Wait for ML model training to complete (~2 minutes)
- ✅ Verify: Model registered in MLflow, `smart_retry_recommendations` table created

### Notebook 05: Dashboards & Genie Examples (1 min)
- Click "Run All"
- Creates SQL views for dashboards
- ✅ Verify: 25+ views created in Gold schema

### Notebook 06/07: Deploy App (Optional)
- **06_app_demo_ui**: Standard single-page app
- **07_advanced_app_ui**: Advanced multi-page app with Genie (RECOMMENDED)
- See `DEPLOYMENT_STRUCTURE.md` for deployment instructions
- ✅ Verify: Query a few views (e.g., `SELECT * FROM gold.v_executive_kpis`)

### Notebook 06: App Demo UI (2 min)
- This notebook deploys a Databricks App
- Click "Deploy as App" in the top-right corner
- Wait for app to deploy (~1 minute)
- Click the app URL to open the Command Center
- ✅ Verify: KPI tiles and charts load successfully

---

## Step 4: Explore the Demo (8 minutes)

### A. View Data Tables

In Databricks SQL or a notebook, run:

```sql
USE CATALOG payments_lakehouse;

-- Bronze tables
SELECT * FROM bronze.transactions_raw LIMIT 10;
SELECT * FROM bronze.cardholders_dim LIMIT 10;
SELECT * FROM bronze.merchants_dim LIMIT 10;

-- Silver tables
SELECT * FROM silver.payments_enriched_stream LIMIT 10;

-- Gold views
SELECT * FROM gold.v_executive_kpis;
SELECT * FROM gold.v_smart_checkout_solution_performance;
SELECT * FROM gold.v_top_decline_reasons;
SELECT * FROM gold.v_retry_recommendation_summary;
```

### B. Explore Databricks App

Open the deployed app and explore:

1. **KPI Dashboard**: Top metrics (approval rate, uplift, risk, value)
2. **Live Transaction Feed**: Recent transactions with filters
3. **Approval Trends**: Hourly trends over 48 hours
4. **Geographic Performance**: Approval rates by country
5. **Solution Performance**: Which solution mixes work best
6. **Decline Analysis**: Top decline reasons with insights
7. **Smart Retry**: Retry recommendations and value recovery
8. **What-If Analysis**: Adjust policy thresholds to see impact

### C. Try Genie Queries (Optional)

If Genie is enabled in your workspace:

1. Open Genie interface
2. Ask natural language questions like:
   - "What is our overall approval rate?"
   - "Show me approval rates by geography"
   - "Which payment solution has the highest approval rate?"
   - "What are the top 5 decline reasons?"

---

## Step 5: Present the Demo (Variable)

Use the demo script in `DEMO_SCRIPT.md` to present the solution:

### Quick Demo (15 min) - Executives
1. Show README business context (5 min)
2. Show Databricks App with KPI tiles and trends (7 min)
3. Highlight business impact: 8-15% approval uplift, $X million recovered (3 min)

### Technical Demo (45 min) - Engineers/Data Scientists
1. Walk through notebooks 01-04 (25 min)
2. Explain architecture with ARCHITECTURE.md (10 min)
3. Show MLflow model and feature importance (5 min)
4. Q&A (5 min)

### Product Demo (30 min) - Product Managers/Analysts
1. Show Databricks App interactively (15 min)
2. Demonstrate What-If analysis (5 min)
3. Show SQL dashboards and Genie queries (5 min)
4. Discuss use cases and customization (5 min)

---

## Troubleshooting

### Issue: Configuration files not found
**Solution**: Verify files uploaded to `dbfs:/payments_demo/config/` with:
```python
dbutils.fs.ls("dbfs:/payments_demo/config/")
```

### Issue: Streaming query fails
**Solution**: Check checkpoint location permissions:
```python
dbutils.fs.ls("dbfs:/payments_demo/checkpoints/")
# If fails, create directory:
dbutils.fs.mkdirs("dbfs:/payments_demo/checkpoints/")
```

### Issue: ML model training slow
**Solution**: Increase cluster size or reduce training data sample:
```python
# In Notebook 04, change:
train_df, test_df = df_ml_features.sample(0.5).randomSplit([0.8, 0.2], seed=42)
```

### Issue: Databricks App won't deploy
**Solution**: 
1. Verify Streamlit is installed: `%pip install streamlit`
2. Check notebook for syntax errors
3. Ensure cluster has sufficient memory (Standard_DS3_v2 or larger)

### Issue: Views return no data
**Solution**: Verify underlying tables populated:
```sql
SELECT COUNT(*) FROM payments_lakehouse.silver.payments_enriched_stream;
-- Should return > 0
```

---

## Next Steps

### Explore Further
- [ ] Add more transactions by re-running Notebook 01
- [ ] Experiment with policy thresholds in the App
- [ ] Create custom SQL queries and dashboards
- [ ] Try Genie natural language queries

### Customize
- [ ] Modify `routing_policies.json` to add new payment solutions
- [ ] Update `reason_codes.json` with your own reason code taxonomy
- [ ] Adjust ML model hyperparameters in Notebook 04

### Deploy to Production
- [ ] Follow `DEPLOYMENT.md` for production deployment checklist
- [ ] Connect to real payment gateway data (replace synthetic data)
- [ ] Set up monitoring and alerting
- [ ] Schedule notebooks as Databricks Workflows

---

## Resources

- **README.md**: Full business story and architecture overview
- **ARCHITECTURE.md**: Detailed technical architecture and data flows
- **DEPLOYMENT.md**: Production deployment checklist
- **DEMO_SCRIPT.md**: Complete demo walkthrough with talking points
- **PROJECT_SUMMARY.md**: High-level deliverables summary

---

## Support

**Questions?** Refer to the documentation or reach out to the project team.

**Feedback?** Let us know how we can improve this demo.

---

## Summary

✅ **In 30 minutes, you:**
1. Uploaded notebooks and configuration files
2. Created Unity Catalog structure
3. Ran 6 notebooks to generate synthetic data and analytics
4. Deployed an interactive Databricks App
5. Explored the demo with sample queries

✅ **You now have:**
- 100K cardholders, 50K merchants, 5K-10K transactions
- Smart Checkout decisions with approval uplift
- Reason Code analytics with actionable insights
- ML-powered Smart Retry recommendations
- Real-time Command Center application

**Ready to present!** 🎉

---

**Last Updated**: 2026-01-30  
**Version**: 1.0  
**Estimated Time**: 30 minutes
