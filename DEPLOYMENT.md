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
  - [ ] `routing_policies.json` → `/Volumes/{CATALOG}/{SCHEMA_BRONZE}/payments_demo/config/`
  - [ ] `retry_policies.json` → `/Volumes/{CATALOG}/{SCHEMA_BRONZE}/payments_demo/config/`
  - [ ] `reason_codes.json` → `/Volumes/{CATALOG}/{SCHEMA_BRONZE}/payments_demo/config/`

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

### Step 7: Databricks App Deployment (15 minutes)

#### Option A: Deploy Advanced App (07_advanced_app_ui.py) - Recommended

**Prerequisites:**
- [ ] Notebooks 00-05 completed successfully
- [ ] Gold tables populated with data
- [ ] Cluster with DBR 13.3 LTS or 14.3 LTS

**Step-by-Step Deployment:**

1. **Navigate to the Notebook**
   - [ ] In Databricks workspace, go to **Workspace** → **Repos** or **Workspace** folder
   - [ ] Open `notebooks/07_advanced_app_ui.py`

2. **Install Required Libraries**
   - [ ] At the top of the notebook, locate the cell:
     ```python
     %pip install streamlit plotly streamlit-extras streamlit-option-menu databricks-sql-connector
     ```
   - [ ] Click **Run Cell** or press `Shift + Enter`
   - [ ] Wait for installation to complete (~30 seconds)
   - [ ] Verify "Successfully installed" message appears

3. **Attach to Cluster**
   - [ ] Click the **Cluster dropdown** at the top of the notebook
   - [ ] Select an existing cluster OR create a new one:
     - **Cluster Name**: `payment-app-cluster`
     - **Cluster Mode**: Single Node
     - **Databricks Runtime**: 14.3 LTS
     - **Node Type**: Standard_DS3_v2 (14 GB Memory, 4 Cores)
     - **Terminate after**: 30 minutes of inactivity
   - [ ] Wait for cluster to start (2-3 minutes)

4. **Test the Notebook Locally (Optional but Recommended)**
   - [ ] Click **Run All** in the notebook
   - [ ] Verify no errors in cell outputs
   - [ ] Scroll to the bottom to see "Run Application" section

5. **Deploy as Databricks App**
   - [ ] At the top-right of the notebook, click **"Apps"** icon (or **"Deploy"** button)
   - [ ] Select **"Create App"** from the dropdown
   - [ ] A dialog box will appear

6. **Configure App Settings**
   
   **App Configuration Dialog:**
   
   - **App Name**: `payment-authorization-command-center`
     - Use lowercase, hyphens only (no spaces or underscores)
   
   - **Source Type**: Select **"Notebook"**
   
   - **Notebook Path**: Should auto-populate with current notebook path
     - Example: `/Workspace/Repos/myname/payment_demo/notebooks/07_advanced_app_ui.py`
   
   - **Compute Configuration**:
     - **Option 1 - Serverless (Recommended)**:
       - [ ] Select **"Serverless"**
       - [ ] No additional config needed
       - [ ] Scales automatically, faster cold starts
     
     - **Option 2 - Existing Cluster**:
       - [ ] Select **"Existing Cluster"**
       - [ ] Choose: `payment-app-cluster` (created in step 3)
       - [ ] Note: Cluster must be running
     
     - **Option 3 - New Job Cluster**:
       - [ ] Select **"New Job Cluster"**
       - [ ] Node Type: Standard_DS3_v2
       - [ ] Workers: 0 (single node)
       - [ ] DBR Version: 14.3 LTS
   
   - **Environment Variables** (Optional):
     - [ ] Add `CATALOG=payments_lakehouse`
     - [ ] Add `SCHEMA_GOLD=gold`
   
   - **Permissions**:
     - [ ] **Can Manage**: Add your email or group
     - [ ] **Can View**: Add stakeholder groups
       - Example: `data-engineering-team@company.com`
       - Example: `executives@company.com`
     - [ ] **Can Run**: Add broader user groups if needed

7. **Deploy the App**
   - [ ] Review all settings
   - [ ] Click **"Create"** button
   - [ ] Deployment starts (this takes 2-5 minutes)
   - [ ] You'll see a progress indicator:
     - "Building app environment..."
     - "Installing dependencies..."
     - "Starting app server..."

8. **Access Your Deployed App**
   - [ ] Once deployed, you'll see: **"App is running"** with a green status
   - [ ] Click the **"Open App"** button OR copy the app URL
   - [ ] App URL format: `https://<workspace>.databricks.com/apps/<app-id>`
   - [ ] Bookmark this URL for easy access

9. **Verify App Functionality**
   - [ ] **Home Page Loads**: Executive dashboard with KPIs
   - [ ] **Sidebar Navigation**: 7 menu items visible
   - [ ] **Data Loading**: Charts and tables populate with data
   - [ ] **Interactivity**: Click through different pages:
     - [ ] Smart Checkout analytics
     - [ ] Decline Analysis
     - [ ] Smart Retry recommendations
     - [ ] Geographic Performance map
     - [ ] Genie AI Assistant
     - [ ] Configuration page
   - [ ] **Filters Work**: Try filtering by geography or date range
   - [ ] **No Errors**: Check browser console (F12) for errors

10. **Share the App**
    - [ ] Click **"Share"** button in the app header
    - [ ] Copy the shareable link
    - [ ] Send to stakeholders via email or Slack
    - [ ] Add to bookmark/favorites for team

#### Option B: Deploy Basic App (06_app_demo_ui.py) - Simpler Alternative

Follow the same steps above, but use `notebooks/06_app_demo_ui.py` instead.
- Simpler single-page interface
- Faster deployment (~1 minute)
- Good for quick demos

**App Management:**

- **View All Apps**: Go to **Workspace** → **Apps** in left sidebar
- **Stop App**: Click app name → **Stop** (saves compute costs)
- **Restart App**: Click **Start** when needed
- **Update App**: Edit notebook → Click **Update App** button
- **Delete App**: Click app name → **Actions** → **Delete**
- **View Logs**: Click app name → **Logs** tab (for troubleshooting)
- **Monitor Usage**: Click app name → **Metrics** tab (views, users, latency)

**Cost Optimization Tips:**
- [ ] Use Serverless compute (auto-scales, pay-per-use)
- [ ] Set app to auto-stop after 30 minutes of inactivity
- [ ] Use smaller cluster for development, scale for production
- [ ] Monitor usage metrics to right-size compute

---

### Step 8: Create Visual Dashboards (30 minutes)

Now create interactive SQL dashboards using the three dashboard SQL files.

#### Dashboard 1: Risk Scoring by Sector/Industry

**Part 1: Create SQL Queries & Views (10 minutes)**

1. **Open Databricks SQL Workspace**
   - [ ] In Databricks workspace, click **"SQL"** in the left sidebar
   - [ ] If prompted, select or create a **SQL Warehouse**:
     - **Name**: `payment-analytics-warehouse`
     - **Cluster Size**: Small (2X-Small for demo)
     - **Auto Stop**: After 10 minutes
     - [ ] Click **"Create"** and wait for warehouse to start (1-2 minutes)

2. **Create New Query**
   - [ ] Click **"Queries"** in the SQL left sidebar
   - [ ] Click **"+ Create Query"** button (top right)
   - [ ] A new SQL editor opens

3. **Load Dashboard SQL File**
   - [ ] Open `dashboards/01_risk_scoring_by_sector.sql` in a text editor
   - [ ] Copy **Query 1: Risk Score Overview by Sector** (lines 17-44)
   - [ ] Paste into Databricks SQL editor
   - [ ] Click **"Run"** (or press Ctrl/Cmd + Enter)
   - [ ] Verify the view is created: "View created successfully"
   - [ ] Click **"Run"** again to see sample data

4. **Save the Query**
   - [ ] Click **"Save"** button (top right)
   - [ ] **Query Name**: `Risk Score Overview by Sector`
   - [ ] **Folder**: Create a new folder called `Payment Analytics Dashboards`
   - [ ] **Description**: "Risk analysis by merchant sector with fraud rates"
   - [ ] Click **"Save"**

5. **Repeat for All 8 Queries**
   - [ ] Create separate queries for:
     - [ ] Query 2: Risk Distribution Histogram
     - [ ] Query 3: Sector Risk Heatmap
     - [ ] Query 4: High-Risk Industry Spotlight
     - [ ] Query 5: Risk Score Trend
     - [ ] Query 6: Risk Mitigation Effectiveness
     - [ ] Query 7: External Risk Signal Impact
     - [ ] Query 8: Risk Score Summary KPIs
   - [ ] Save each with descriptive names

**Part 2: Build the Visual Dashboard (20 minutes)**

1. **Create New Dashboard**
   - [ ] Click **"Dashboards"** in the SQL left sidebar
   - [ ] Click **"+ Create Dashboard"** button
   - [ ] **Dashboard Name**: `Risk Scoring by Sector & Industry`
   - [ ] **Description**: "Real-time risk analytics across merchant sectors with fraud monitoring"
   - [ ] Click **"Create"**

2. **Add KPI Cards (Query 8)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `Risk Score Summary KPIs`
   - [ ] Click **"Add to Dashboard"**
   - [ ] A widget appears on the canvas
   - [ ] Click the **widget settings** (gear icon)
   - [ ] **Visualization Type**: Select **"Counter"**
   - [ ] Configure counter:
     - **Counter Label**: "Overall Avg Risk Score"
     - **Counter Value Column**: `overall_avg_risk_score`
     - **Target Value**: 0.30 (low risk target)
     - **Format**: Number with 3 decimals
   - [ ] Repeat for other KPIs: `p90_risk_score`, `pct_high_risk`, `fraud_attempt_rate`
   - [ ] Position KPI cards in a row at the top (drag and drop)
   - [ ] Resize to be small and uniform

3. **Add Bar Chart (Query 1)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `Risk Score Overview by Sector`
   - [ ] Click **"Add to Dashboard"**
   - [ ] Click **"Edit Visualization"** on the widget
   - [ ] **Visualization Type**: **"Bar"**
   - [ ] **X Column**: `merchant_sector`
   - [ ] **Y Columns**: `avg_risk_score`
   - [ ] **Group By**: None
   - [ ] Click **"Colors"** tab:
     - [ ] Enable **"Color by Value"**
     - [ ] Map to column: `high_risk_percentage`
     - [ ] Color scheme: "Reds" (low to high)
   - [ ] Click **"Axes"** tab:
     - [ ] X-axis label: "Merchant Sector"
     - [ ] Y-axis label: "Average Risk Score"
     - [ ] Enable Y-axis grid lines
   - [ ] Click **"Save"**
   - [ ] Position below KPI cards (left side)

4. **Add Stacked Bar Chart (Query 2)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `Risk Distribution Histogram`
   - [ ] **Visualization Type**: **"Bar"**
   - [ ] **X Column**: `risk_bucket`
   - [ ] **Y Columns**: `transaction_count`
   - [ ] **Group By**: `merchant_sector`
   - [ ] **Stacking**: Enable "Stack bars"
   - [ ] **Colors**: Use "Spectral" color scheme
   - [ ] Position below KPI cards (right side, next to bar chart)

5. **Add Heatmap (Query 3)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `Sector Risk Heatmap`
   - [ ] Click **"Edit Visualization"**
   - [ ] **Visualization Type**: **"Heatmap"** (if available) OR **"Table"**
   - [ ] For Table visualization:
     - [ ] Enable **"Conditional Formatting"**
     - [ ] Column: `avg_risk_score`
     - [ ] Format: Color scale (White → Yellow → Red)
     - [ ] Min: 0.0, Max: 1.0
   - [ ] Position in middle row

6. **Add Line Chart (Query 5)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `Risk Score Trend`
   - [ ] **Visualization Type**: **"Line"**
   - [ ] **X Column**: `date`
   - [ ] **Y Columns**: `avg_risk_score`
   - [ ] **Group By**: `merchant_sector`
   - [ ] Enable **"Series Stacking"**: None
   - [ ] **Line Style**: Smooth
   - [ ] **Show Points**: Yes
   - [ ] **Legend Position**: Right
   - [ ] Position at bottom of dashboard

7. **Add Table (Query 4)**
   - [ ] Click **"+ Add"** → **"Visualization"**
   - [ ] Select query: `High-Risk Industry Spotlight`
   - [ ] **Visualization Type**: **"Table"**
   - [ ] Click **"Columns"** tab:
     - [ ] Show: All columns
     - [ ] Enable sorting
     - [ ] Enable search/filter
   - [ ] Click **"Formatting"** tab:
     - [ ] `avg_risk_score`: Color scale (green to red)
     - [ ] `decline_rate`: Color scale (green to red)
     - [ ] `pct_using_3ds`: Color scale (red to green - higher is better)
   - [ ] Position in a dedicated row

8. **Add Dashboard Filters**
   - [ ] Click **"Add"** → **"Date Range Filter"**
   - [ ] **Default Range**: "Last 7 days"
   - [ ] **Options**: Last 1/7/14/30 days, Custom range
   - [ ] Apply to all queries
   - [ ] Position at the very top
   
   - [ ] Click **"Add"** → **"Dropdown Filter"**
   - [ ] **Filter Name**: "Merchant Sector"
   - [ ] **Query**: Use Query 1
   - [ ] **Column**: `merchant_sector`
   - [ ] **Allow Multiple**: Yes
   - [ ] **Default**: All
   - [ ] Position next to date filter

9. **Configure Dashboard Layout**
   - [ ] Drag and drop widgets to arrange them logically
   - [ ] Resize widgets for optimal viewing:
     - KPI cards: Small (1/4 width each)
     - Charts: Medium (1/2 width) or Large (full width)
     - Tables: Full width
   - [ ] Add **Text Boxes** for section headers:
     - [ ] "Risk Overview"
     - [ ] "Industry Analysis"
     - [ ] "Trend Analysis"
   - [ ] Ensure consistent spacing and alignment

10. **Set Dashboard Refresh Schedule**
    - [ ] Click **"Schedule"** (top right)
    - [ ] Enable **"Auto Refresh"**
    - [ ] **Refresh Interval**: Every 5 minutes
    - [ ] **Active Hours**: 24/7 or business hours only
    - [ ] Click **"Save"**

11. **Publish Dashboard**
    - [ ] Click **"Publish"** button (top right)
    - [ ] Dashboard is now live and shareable
    - [ ] Copy the **Dashboard URL**

12. **Share Dashboard**
    - [ ] Click **"Share"** button
    - [ ] **Manage Permissions** dialog opens:
       - [ ] Add users/groups who **Can Edit**
       - [ ] Add users/groups who **Can Run** (view and refresh)
       - [ ] Add users/groups who **Can View** (read-only)
    - [ ] Enable **"Public Link"** if needed (external sharing)
    - [ ] Click **"Done"**

**Dashboard 1 Complete! ✅**

#### Dashboard 2: Transactions by Country

Repeat the same process using `dashboards/02_transactions_by_country.sql`:

1. **Create 9 SQL Queries** (same as Dashboard 1, Part 1)
2. **Create Dashboard**: `Transaction Volume by Country`
3. **Add Visualizations**:
   - [ ] KPI Cards (Query 8) - Total countries, transactions, volume, growth
   - [ ] **Map Visualization** (Query 1) - Critical step:
     - [ ] **Visualization Type**: **"Map"** or **"Choropleth"**
     - [ ] **Location Column**: `country_code` (must be ISO country codes)
     - [ ] **Value Column**: `total_volume_usd`
     - [ ] **Color Scale**: Blues or Greens (higher = darker)
     - [ ] **Tooltip Columns**: `country_name`, `total_transactions`, `approval_rate`
   - [ ] Horizontal Bar Chart (Query 2) - Top 20 countries with growth arrows
   - [ ] Multi-line Chart (Query 3) - Daily trends
   - [ ] Sankey/Flow Diagram (Query 4) - Cross-border flows
     - Note: If Sankey not available, use grouped bar chart as alternative
   - [ ] Grouped Bar Chart (Query 5) - Regional performance
   - [ ] Stacked Bar Chart (Query 6) - Channel breakdown
   - [ ] Heatmap (Query 7) - Hourly patterns
4. **Add Filters**:
   - [ ] Date Range (last 30 days default)
   - [ ] Country/Region multi-select
   - [ ] Channel (online/mobile/pos)
5. **Publish & Share**

**Dashboard 2 Complete! ✅**

#### Dashboard 3: Standard vs Optimized Approval Rates

Repeat the same process using `dashboards/03_standard_vs_optimized_approval_rates.sql`:

1. **Create 9 SQL Queries**
2. **Create Dashboard**: `Standard vs Optimized Approval Rates`
3. **Add Visualizations**:
   - [ ] KPI Cards (Query 9) - Uplift %, revenue gain, ROI
   - [ ] **Comparison Bars** (Query 1):
     - [ ] **Visualization Type**: **"Bar"**
     - [ ] Show baseline vs optimized side-by-side
     - [ ] Use contrasting colors (grey vs green)
   - [ ] **Dual-Line Chart** (Query 4):
     - [ ] Two lines: baseline vs optimized approval rates
     - [ ] **Fill Area Between Lines**: Enable if available (shows uplift gap)
     - [ ] Color: Grey (baseline), Green (optimized)
   - [ ] **Scatter Plot** (Query 3):
     - [ ] X: `cost_per_transaction_usd`
     - [ ] Y: `approval_rate`
     - [ ] Size: `total_transactions`
     - [ ] Color: `solution_category`
     - [ ] Add quadrant lines at (0.20, 85%) - ideal zone
   - [ ] **Area Chart** (Query 5):
     - [ ] X: `date`
     - [ ] Y: `daily_revenue_uplift` (area fill)
     - [ ] Secondary Y: `cumulative_revenue_uplift` (line)
   - [ ] **Lollipop/Diverging Bar** (Query 6):
     - [ ] Horizontal bars showing uplift by geography
     - [ ] Green for positive, Red for negative
   - [ ] **Waterfall Chart** (Query 7):
     - [ ] Shows cascading recovery flow
     - [ ] Start → Attempt → Success → Fail
   - [ ] **Table with Confidence Intervals** (Query 8):
     - [ ] A/B test results
     - [ ] Show statistical significance badge
     - [ ] Color-code recommendation column
4. **Add Filters**:
   - [ ] Time Period (7/14/30/90 days)
   - [ ] Geography
   - [ ] Solution Type
   - [ ] Transaction Amount Range (slider)
5. **Add Text Annotations**:
   - [ ] "✅ Statistical Significance: p < 0.05"
   - [ ] "🎯 Target: +2-5% approval uplift"
   - [ ] "💰 ROI: 10x revenue vs cost"
6. **Publish & Share**

**Dashboard 3 Complete! ✅**

#### Dashboard Best Practices

**Design Tips:**
- [ ] Use consistent color schemes across dashboards
- [ ] Keep KPIs at the top for quick scanning
- [ ] Group related visualizations together
- [ ] Add white space between sections
- [ ] Use descriptive titles for each widget
- [ ] Add tooltips/descriptions for complex metrics

**Performance Optimization:**
- [ ] Use materialized views for complex queries
- [ ] Cache frequently accessed data
- [ ] Limit date ranges with filters
- [ ] Use smaller SQL Warehouse for development
- [ ] Pre-aggregate data in Gold layer

**Maintenance:**
- [ ] Set up **Dashboard Alerts**:
  - [ ] Approval rate drops below 80%
  - [ ] Fraud rate exceeds 2%
  - [ ] Data freshness > 10 minutes
- [ ] Schedule **Email Reports**:
  - [ ] Daily executive summary
  - [ ] Weekly performance report
  - [ ] Monthly trend analysis
- [ ] **Version Control**:
  - [ ] Export dashboard JSON periodically
  - [ ] Document any changes in CHANGELOG

**Troubleshooting Dashboard Issues:**

1. **"No data" or empty visualizations**:
   - [ ] Check that underlying queries return data
   - [ ] Verify date filters are not too restrictive
   - [ ] Ensure SQL Warehouse is running
   - [ ] Check table/view permissions

2. **Slow dashboard loading**:
   - [ ] Reduce date range
   - [ ] Add WHERE clauses to filter data early
   - [ ] Use Delta table optimization (OPTIMIZE, ZORDER)
   - [ ] Upgrade SQL Warehouse size

3. **Visualization not displaying correctly**:
   - [ ] Verify column names match exactly
   - [ ] Check data types (dates, numbers)
   - [ ] Try different visualization type
   - [ ] Clear browser cache

4. **Auto-refresh not working**:
   - [ ] Verify schedule is enabled
   - [ ] Check SQL Warehouse auto-stop settings
   - [ ] Ensure queries don't time out

**All Dashboards Complete! 🎉**

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
2. **Delete checkpoint files**: `%sh rm -r /Volumes/{CATALOG}/{SCHEMA_BRONZE}:/payments_demo/checkpoints/`
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
