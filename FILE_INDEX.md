# 📁 File Index & Navigation Guide

## Project Structure

```
accelerate_approvals_demo/
│
├── 📘 QUICKSTART.md                    ⭐ START HERE - 30-minute setup guide
├── 📘 README.md                        📖 Complete business story & architecture overview
├── 📘 PROJECT_SUMMARY.md               ✅ Deliverables checklist & completion status
├── 📘 ARCHITECTURE.md                  🏗️ Detailed technical architecture & data flows
├── 📘 DEPLOYMENT.md                    🚀 Production deployment checklist & validation
├── 📘 DEPLOYMENT_STRUCTURE.md          📦 Databricks App deployment file structure guide
├── 📘 DEMO_SCRIPT.md                   🎤 45-minute demo script with talking points
├── 📘 PRESENTATION.md                  🎯 Executive presentation content
├── 📘 PRESENTATION_GUIDE.md            🗣️ How to present the solution
├── 📘 FILE_INDEX.md                    📁 This file - navigation guide
├── 📘 LICENSE                          📜 Project license
│
├── 🔧 app.yaml                         ⚙️ Databricks App configuration (ROOT)
├── 🔧 requirements.txt                 📦 Python dependencies (ROOT)
│
├── 📂 notebooks/                       💻 Databricks notebooks & apps
│   ├── 00_deployment_setup.py                         [Setup & Validation]
│   ├── 01_ingest_synthetic_data.py                    [Bronze Layer]
│   ├── 02_stream_enrichment_smart_checkout.py         [Silver Layer]
│   ├── 03_reason_code_performance.py                  [Gold - Analytics]
│   ├── 04_smart_retry.py                              [Gold - ML]
│   ├── 05_dashboards_and_genie_examples.sql           [Dashboards]
│   ├── 📂 06_demo_app/
│   │   └── 06_app_demo_ui.py                          [Standard Interactive App]
│   └── 📂 07_advanced_app/
│       └── 07_advanced_app_ui.py                      [Advanced Multi-page App] ⭐ RECOMMENDED
│
├── 📂 dashboards/                      📊 Databricks SQL dashboard definitions
│   ├── 01_risk_scoring_by_sector.sql                  [Risk & Sector Analytics]
│   ├── 02_transactions_by_country.sql                 [Geographic Analytics]
│   └── 03_standard_vs_optimized_approval_rates.sql    [Approval Rate Comparison]
│
├── 📂 resources/                       ⚙️ Configuration & SQL resources
│   ├── 📂 config/                      🔧 JSON configuration files
│   │   ├── routing_policies.json                      [Smart Checkout config]
│   │   ├── retry_policies.json                        [Smart Retry config]
│   │   ├── reason_codes.json                          [Reason code taxonomy]
│   │   └── policies.json                              [Master policy config]
│   ├── 📂 sql/                         📊 SQL views for dashboards
│   │   └── dashboard_views.sql                        [Additional SQL views]
│   └── 📂 app_settings/                🎨 Legacy app config (deprecated)
│       ├── app.yaml                                   [Use root app.yaml instead]
│       └── requirements.txt                           [Use root requirements.txt instead]
│
├── 📂 .cursor/                         🔧 Cursor IDE configuration
│   ├── packages.json                                  [Project metadata]
│   ├── app.yaml                                       [Deprecated - use root]
│   └── requirements.txt                               [Deprecated - use root]
│
└── 📂 data/                            💾 Generated at runtime
    └── (synthetic data created when notebooks run)
```

---

## 🚀 Deployment Files (Root Directory)

### app.yaml ⚙️
**Location:** `/app.yaml` (root directory)  
**Purpose:** Databricks App configuration file  
**When to use:** Required for deploying Streamlit apps to Databricks  

**Key sections:**
- Command configuration for Streamlit
- Environment variables (catalog names, feature flags)
- Resource allocation (CPU, memory)
- Health check settings
- App metadata and tags

**Important notes:**
- Must be in same directory as `app.py` and `requirements.txt`
- Contains comprehensive environment configuration
- See `DEPLOYMENT_STRUCTURE.md` for deployment instructions

### requirements.txt 📦
**Location:** `/requirements.txt` (root directory)  
**Purpose:** Python package dependencies for Databricks App  
**When to use:** Required for all Databricks App deployments  

**Includes:**
- Streamlit framework and extensions
- Data processing libraries (pandas, numpy)
- Databricks connectors (SQL, SDK)
- Visualization libraries (plotly, altair, matplotlib)
- ML libraries (scikit-learn, mlflow)
- Configuration parsers (PyYAML)

**Installation:**
```bash
# Local development
pip install -r requirements.txt

# Databricks automatically installs from this file during deployment
```

### ⚠️ Legacy Files (Deprecated)
These files exist for backward compatibility but should NOT be used:
- `.cursor/app.yaml` → Use `/app.yaml` instead
- `.cursor/requirements.txt` → Use `/requirements.txt` instead  
- `resources/app_settings/app.yaml` → Use `/app.yaml` instead
- `resources/app_settings/requirements.txt` → Use `/requirements.txt` instead

---

## 📚 Documentation Guide

### For First-Time Users
**Start with these in order:**
1. 📘 **QUICKSTART.md** - Get up and running in 30 minutes
2. 📘 **README.md** - Understand the business context and solution
3. 🎤 **DEMO_SCRIPT.md** - Learn how to present the demo

### For Technical Deep-Dive
**Read these for detailed understanding:**
1. 🏗️ **ARCHITECTURE.md** - System design, data flows, technology stack
2. 🚀 **DEPLOYMENT.md** - Production deployment procedures
3. 💻 **Notebooks** - Code implementation details

### For Project Management
**Track progress with:**
1. ✅ **PROJECT_SUMMARY.md** - High-level deliverables overview
2. 🚀 **DEPLOYMENT.md** - Deployment checklist

---

## 💻 Notebook Guide

### Execution Order (MUST follow this sequence)

| # | Notebook | Layer | Purpose | Time | Output |
|---|----------|-------|---------|------|--------|
| 0 | `00_deployment_setup.py` | Setup | Create catalogs, schemas, configs | 2 min | Unity Catalog structure, config files |
| 1 | `01_ingest_synthetic_data.py` | Bronze | Generate synthetic transaction data | 3 min | 100K cardholders, 50K merchants, 5K-10K transactions |
| 2 | `02_stream_enrichment_smart_checkout.py` | Silver | Enrich transactions & apply Smart Checkout | 3 min | `payments_enriched_stream` with solution recommendations |
| 3 | `03_reason_code_performance.py` | Gold | Analyze declines & generate insights | 2 min | 10+ Gold tables with decline analytics |
| 4 | `04_smart_retry.py` | Gold | Train ML model & generate retry recommendations | 4 min | ML model + `smart_retry_recommendations` table |
| 5 | `05_dashboards_and_genie_examples.sql` | Gold | Create SQL views for dashboards | 1 min | 25+ SQL views |
| 6a | `06_demo_app/06_app_demo_ui.py` | App | Deploy standard interactive app | 2 min | Databricks App URL |
| 6b | `07_advanced_app/07_advanced_app_ui.py` | App | Deploy advanced multi-page app ⭐ | 2 min | Databricks App URL |

### Notebook Details

#### 00_deployment_setup.py 🆕
**What it does:**
- Creates Unity Catalog structure (catalog + schemas)
- Sets up DBFS directories for data and configs
- Generates and uploads configuration JSON files
- Configures MLflow experiment tracking
- Validates environment and provides cluster recommendations

**Key outputs:**
- `payments_lakehouse` catalog with bronze/silver/gold schemas
- Configuration files in DBFS
- MLflow experiment setup
- Environment validation report

**When to use:** Run first before any other notebooks. One-time setup.

---

#### 01_ingest_synthetic_data.py
**What it does:**
- Generates 100,000 synthetic cardholders with KYC segments
- Creates 50,000 merchants with MCC codes and risk profiles
- Generates external risk signals (Moody's-style macro data)
- Streams synthetic transactions with payment solution flags

**Key outputs:**
- `cardholders_dim` (100,000 rows)
- `merchants_dim` (50,000 rows)
- `external_risk_signals` (~105 rows)
- `transactions_raw` (streaming, 5,000-10,000+ rows)

**When to use:** First notebook to run. Generates foundational data.

---

#### 02_stream_enrichment_smart_checkout.py
**What it does:**
- Joins transactions with cardholder, merchant, and risk data
- Engineers features (velocity, behavior, temporal)
- Evaluates 50+ payment solution combinations
- Selects optimal solution mix per transaction
- Generates cascading path for fallback routing

**Key outputs:**
- `payments_enriched_stream` with Smart Checkout decisions

**When to use:** After Notebook 01. Applies Smart Checkout decisioning.

---

#### 03_reason_code_performance.py
**What it does:**
- Aggregates declines by issuer, geography, merchant, channel, solution
- Generates actionable insights with root cause analysis
- Creates decline heatmaps and trend visualizations
- Produces configuration recommendations for Smart Checkout

**Key outputs:**
- `decline_distribution`, `decline_by_issuer`, `decline_by_geography`
- `reason_code_insights` with actionable recommendations
- `decline_heatmap_issuer_reason`

**When to use:** After Notebook 02. Analyzes decline patterns.

---

#### 04_smart_retry.py
**What it does:**
- Generates synthetic retry history with outcomes
- Trains Gradient Boosted Trees model to predict retry success
- Evaluates model performance (AUC, accuracy, feature importance)
- Generates retry recommendations (RETRY_NOW, RETRY_LATER, DO_NOT_RETRY)
- Calculates optimal retry timing and estimated value recovery

**Key outputs:**
- MLflow registered model: `smart_retry_classifier`
- `retry_history` (Silver layer)
- `smart_retry_recommendations` (Gold layer)
- `retry_model_feature_importance`

**When to use:** After Notebook 03. Adds ML-powered retry optimization.

---

#### 05_dashboards_and_genie_examples.sql
**What it does:**
- Creates 25+ SQL views for dashboards
- Executive KPIs, geographic performance, solution analytics
- Decline analysis views with actionable insights
- Smart Retry metrics and value recovery views
- Provides Genie natural language query examples

**Key outputs:**
- `v_executive_kpis`, `v_approval_trends_hourly`
- `v_smart_checkout_solution_performance`
- `v_top_decline_reasons`, `v_actionable_insights_summary`
- `v_retry_recommendation_summary`

**When to use:** After Notebook 04. Creates views for dashboards and Genie.

---

#### 06_app_demo_ui.py (Standard App)
**What it does:**
- Deploys interactive Databricks App with Streamlit
- Real-time KPI dashboard with 5 key metrics
- Live transaction feed with filtering
- Interactive charts (bar, line, pie, scatter, Sankey)
- What-if analysis with policy threshold controls
- Auto-refresh capability (10-second intervals)

**Key features:**
- Single-page dashboard layout
- Real-time data refresh
- Geographic heatmap
- Solution mix analyzer
- Decline trend analysis
- What-if scenario modeling

**Key outputs:**
- Databricks App URL (accessible via web browser)

**When to use:** After Notebook 05. Provides interactive UI for live monitoring.

**Deployment:** See `DEPLOYMENT_STRUCTURE.md` for instructions on copying to root as `app.py`

---

#### 07_advanced_app_ui.py (Advanced Multi-Page App) ⭐ RECOMMENDED
**What it does:**
- Professional multi-page Streamlit app with enhanced UI
- Sidebar navigation with 7 dedicated pages
- Advanced visualizations with Plotly and custom CSS
- Genie AI integration for natural language queries
- Configuration management interface
- Enhanced filtering and real-time updates

**Pages:**
1. **🏠 Executive Dashboard** - High-level KPIs and trends
2. **🎯 Smart Checkout** - Solution optimization and A/B testing
3. **📉 Decline Analysis** - Issuer heatmaps and actionable insights
4. **🔄 Smart Retry** - Retry recommendation engine with ROI calculator
5. **🌍 Geographic Performance** - Global transaction map and regional analysis
6. **🤖 Genie AI Assistant** - Natural language query interface with example prompts
7. **⚙️ Configuration** - Policy management and threshold adjustments

**Key features:**
- Professional UI with custom CSS styling
- Multi-page navigation via sidebar
- Enhanced data visualization (Plotly choropleth maps, sunburst charts)
- Genie AI integration for natural language analytics
- Real-time KPI cards with trend indicators
- Interactive filters (date range, geography, channel, risk level)
- Configuration management panel
- Mobile-responsive design

**Key outputs:**
- Databricks App URL with multi-page interface

**When to use:** After Notebook 05. **Recommended over standard app** for full feature set.

**Deployment:** See `DEPLOYMENT_STRUCTURE.md` for instructions on copying to root as `app.py`

**Advantages over 06_app_demo_ui.py:**
- ✅ Multi-page navigation vs single page
- ✅ Genie AI integration
- ✅ Professional UI/UX design
- ✅ Configuration management interface
- ✅ Enhanced visualizations
- ✅ Better mobile responsiveness
- ✅ More comprehensive analytics

---

## 📊 Databricks SQL Dashboards (3 Visual Dashboards)

### 01_risk_scoring_by_sector.sql
**What it creates:**
- 8 SQL views for risk analytics by merchant sector/industry
- Visual dashboard with bar charts, heatmaps, and trend lines

**Key views:**
- Risk overview by sector/category
- Risk distribution analysis
- Hourly risk heatmaps
- High-risk spotlight tables
- Risk trend analysis (7-day)
- Mitigation effectiveness metrics
- External risk signal impact
- Risk vs. approval rate correlation

**When to use:** Create visual dashboard in Databricks SQL Workspace

---

### 02_transactions_by_country.sql
**What it creates:**
- 9 SQL views for geographic transaction analysis
- Visual dashboard with choropleth maps and regional breakdowns

**Key views:**
- Global transaction volume map
- Top countries by volume/approval rate
- Daily transaction trends by country
- Cross-border flow analysis (Sankey diagram)
- Regional performance comparison
- Transaction volume by channel and country
- Country rank over time
- Hourly pattern heatmap by country
- Country performance scorecard

**When to use:** Create visual dashboard in Databricks SQL Workspace

---

### 03_standard_vs_optimized_approval_rates.sql
**What it creates:**
- 9 SQL views comparing baseline vs. optimized approval performance
- Visual dashboard with KPI cards, comparison bars, and uplift metrics

**Key views:**
- Overall approval rate comparison (KPI cards)
- Segmented uplift by geography/channel/issuer
- Solution mix performance comparison
- Time series approval rate trends
- Revenue impact and incremental value
- Geographic uplift heatmap
- Cascading effectiveness analysis
- Retry impact on approval rates
- A/B test results (control vs. optimized)

**When to use:** Create visual dashboard in Databricks SQL Workspace

**Deployment:** See `DEPLOYMENT.md` Section 8 for step-by-step dashboard creation guide

---

## ⚙️ Configuration Files

### routing_policies.json
**Purpose:** Smart Checkout configuration  
**Location:** `resources/config/routing_policies.json`  
**Upload to:** `dbfs:/payments_demo/config/routing_policies.json`

**Contains:**
- Payment solution definitions (3DS, Antifraud, IDPay, DataShareOnly, NetworkToken, Passkey)
- Approval impact, risk reduction, cost per solution
- Cascading rules by decline code
- Merchant constraints (high-risk MCCs)
- Issuer routing preferences
- Risk thresholds (low, medium, high, critical)

**When to modify:** To add new payment solutions or adjust business rules

---

### retry_policies.json
**Purpose:** Smart Retry configuration  
**Location:** `resources/config/retry_policies.json`  
**Upload to:** `dbfs:/payments_demo/config/retry_policies.json`

**Contains:**
- Retry strategies (recurring payments, cardholder-initiated)
- Max attempts, backoff schedules
- Optimal retry windows (salary days, business hours)
- Decline code retry rules (which codes are retryable)
- Issuer-specific rules (optimal hours, weekend avoidance)
- ML model configuration (features, thresholds)

**When to modify:** To adjust retry timing or ML model parameters

---

### reason_codes.json
**Purpose:** Reason code taxonomy  
**Location:** `resources/config/reason_codes.json`  
**Upload to:** `dbfs:/payments_demo/config/reason_codes.json`

**Contains:**
- Standardized 12 reason codes with descriptions
- Categories (Soft Decline, Hard Decline, Technical, Security)
- Severity levels (none, low, medium, high, critical)
- Actionability flags
- Root causes for each code
- Recommended actions for remediation
- Analytics segments

**When to modify:** To customize reason code taxonomy or add new codes

---

## 📊 SQL Views (25+ Total)

### Executive & KPI Views
- `v_executive_kpis` - High-level metrics
- `v_approval_trends_hourly` - Time-series trends
- `v_performance_by_geography` - Geographic breakdown
- `v_realtime_kpi_snapshot` - Real-time snapshot
- `v_performance_vs_baseline` - Comparison metrics

### Smart Checkout Views
- `v_smart_checkout_solution_performance` - Solution mix effectiveness
- `v_solution_performance_by_geography` - Geographic solution analysis
- `v_solution_performance_by_issuer` - Issuer-specific performance
- `v_solution_performance_by_channel` - Channel analysis
- `v_top_solution_mixes` - Best performing solutions

### Reason Code Views
- `v_top_decline_reasons` - Top decline codes with taxonomy
- `v_actionable_insights_summary` - Prioritized insights
- `v_decline_trends_analysis` - Time-series decline data
- Plus 4 more aggregation views

### Smart Retry Views
- `v_retry_recommendation_summary` - Retry action distribution
- `v_retry_by_reason_code` - Recommendations by decline code
- `v_retry_value_recovery` - Estimated financial recovery

### Cross-Functional Views
- `v_approval_funnel` - Transaction funnel analysis
- `v_risk_approval_matrix` - Risk vs approval performance
- `v_merchant_segment_performance` - Merchant cluster analysis
- `v_last_hour_performance` - Recent performance
- `v_active_alerts` - Real-time alerting

---

## 🎯 Usage Scenarios

### Scenario 1: Quick Demo (15 min)
**Files needed:**
- 📘 README.md (business context)
- 💻 Notebook 06 (Databricks App)

**Steps:**
1. Open README, show business problem (2 min)
2. Show Databricks App with KPI tiles (8 min)
3. Highlight approval uplift and value recovery (5 min)

---

### Scenario 2: Technical Deep-Dive (45 min)
**Files needed:**
- 🏗️ ARCHITECTURE.md
- 💻 All notebooks (01-06)

**Steps:**
1. Explain architecture (10 min)
2. Walk through notebooks 01-04 (25 min)
3. Show MLflow model and feature importance (5 min)
4. Q&A (5 min)

---

### Scenario 3: Hands-On Workshop (2 hours)
**Files needed:**
- 📘 QUICKSTART.md
- 💻 All notebooks (01-06)
- ⚙️ All configuration files

**Steps:**
1. Participants follow QUICKSTART to deploy (30 min)
2. Explore data and query tables (30 min)
3. Modify configuration files and re-run (30 min)
4. Customize dashboards and App (30 min)

---

### Scenario 4: Production Deployment (1-2 weeks)
**Files needed:**
- 🚀 DEPLOYMENT.md
- 🏗️ ARCHITECTURE.md
- 💻 All notebooks
- ⚙️ All configuration files

**Steps:**
1. Follow deployment checklist (1-2 days)
2. Connect to real data sources (2-3 days)
3. Tune ML model with production data (1-2 days)
4. Set up monitoring and alerting (1-2 days)
5. User acceptance testing (2-3 days)
6. Production rollout (1 day)

---

## 🔍 Finding What You Need

### "I want to understand the business case"
→ Read: 📘 **README.md** (Business Context section)

### "I want to run the demo quickly"
→ Follow: 📘 **QUICKSTART.md** (30-minute guide)

### "I want to understand the technical architecture"
→ Read: 🏗️ **ARCHITECTURE.md** (Detailed architecture)

### "I want to deploy to production"
→ Follow: 🚀 **DEPLOYMENT.md** (Deployment checklist)

### "I want to present this to stakeholders"
→ Use: 🎤 **DEMO_SCRIPT.md** (45-minute script)

### "I want to customize payment solutions"
→ Edit: ⚙️ **resources/config/routing_policies.json**

### "I want to modify retry logic"
→ Edit: ⚙️ **resources/config/retry_policies.json**

### "I want to add a new reason code"
→ Edit: ⚙️ **resources/config/reason_codes.json**

### "I want to see the code for Smart Checkout"
→ Open: 💻 **notebooks/02_stream_enrichment_smart_checkout.py**

### "I want to see the ML model code"
→ Open: 💻 **notebooks/04_smart_retry.py**

### "I want to create a custom dashboard"
→ Use: 📊 **resources/sql/dashboard_views.sql** as examples

---

## 📦 Complete File Listing

```
📘 Documentation (7 files)
├── QUICKSTART.md           (8 KB)  - 30-minute setup guide
├── README.md               (32 KB) - Complete business story
├── PROJECT_SUMMARY.md      (11 KB) - Deliverables summary
├── ARCHITECTURE.md         (28 KB) - Technical architecture
├── DEPLOYMENT.md           (8 KB)  - Deployment checklist
├── DEMO_SCRIPT.md          (13 KB) - Demo walkthrough
└── LICENSE                 (1 KB)  - Project license

💻 Notebooks (6 files, ~600 KB total)
├── 01_ingest_synthetic_data.py                (85 KB)
├── 02_stream_enrichment_smart_checkout.py     (120 KB)
├── 03_reason_code_performance.py              (95 KB)
├── 04_smart_retry.py                          (130 KB)
├── 05_dashboards_and_genie_examples.sql       (70 KB)
└── 06_app_demo_ui.py                          (100 KB)

⚙️ Configuration (3 files, ~35 KB total)
├── routing_policies.json   (12 KB)
├── retry_policies.json     (10 KB)
└── reason_codes.json       (13 KB)

📊 SQL Resources (1 file)
└── dashboard_views.sql     (5 KB)
```

**Total: 17 files, ~720 KB**

---

## ✅ Quick Reference

### Most Important Files
1. 📘 **QUICKSTART.md** - Start here!
2. 📘 **README.md** - Understand the "why"
3. 💻 **notebooks/01-06** - Run these in order
4. 🎤 **DEMO_SCRIPT.md** - Present with this

### File Size Summary
- **Documentation**: ~100 KB (7 files)
- **Notebooks**: ~600 KB (6 files)
- **Configuration**: ~35 KB (3 files)
- **SQL**: ~5 KB (1 file)

---

**Last Updated**: 2026-01-30  
**Version**: 1.0  
**Total Files**: 17
