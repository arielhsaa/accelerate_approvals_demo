# 🚀 Quick Deployment Guide - Premium App

## File Created
✅ **`notebooks/08_premium_app/08_premium_app_ui.py`** (62 KB, 1,500+ lines)

## 🎯 Quick Deploy (3 Methods)

### Method 1: Databricks CLI (Fastest) ⚡

```bash
# Create and prepare deployment package
mkdir -p /tmp/payment-app-premium
cp notebooks/08_premium_app/08_premium_app_ui.py /tmp/payment-app-premium/app.py
cp app.yaml /tmp/payment-app-premium/
cp requirements.txt /tmp/payment-app-premium/

# Upload to Databricks workspace
databricks workspace import-dir /tmp/payment-app-premium \
  /Workspace/Users/<your-email>/payment-authorization-premium --overwrite

# Deploy the app
databricks apps deploy payment-authorization-premium \
  --source-code-path /Workspace/Users/<your-email>/payment-authorization-premium

# Access your app
databricks apps get payment-authorization-premium
```

---

### Method 2: Databricks UI (Most Visual) 🖱️

**Step 1: Create Workspace Folder**
1. Navigate to **Workspace** → **Users** → `<your-email>`
2. Click **Create** → **Folder**
3. Name it: `payment-authorization-premium`

**Step 2: Upload Files**
1. Open the folder you just created
2. Click **Import**
3. Upload these 3 files:
   - `notebooks/08_premium_app/08_premium_app_ui.py` → **Rename to `app.py`**
   - `app.yaml` (from root)
   - `requirements.txt` (from root)

**Step 3: Deploy App**
1. Go to **Apps** (left sidebar)
2. Click **Create App**
3. **App Name:** `payment-authorization-premium`
4. **Source Code Path:** `/Workspace/Users/<your-email>/payment-authorization-premium`
5. Click **Create**
6. Wait 2-3 minutes for deployment
7. Click the app URL when ready!

---

### Method 3: Python Script (Automated) 🤖

```python
# deploy_premium_app.py
import os
import shutil
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Your email
USER_EMAIL = "your.email@company.com"  # UPDATE THIS
WORKSPACE_PATH = f"/Workspace/Users/{USER_EMAIL}/payment-authorization-premium"

print("🚀 Deploying Premium Payment Authorization App...")

# Step 1: Prepare local deployment directory
print("📦 Step 1/4: Preparing files...")
local_dir = "/tmp/payment-app-premium"
os.makedirs(local_dir, exist_ok=True)

shutil.copy("notebooks/08_premium_app/08_premium_app_ui.py", f"{local_dir}/app.py")
shutil.copy("app.yaml", f"{local_dir}/app.yaml")
shutil.copy("requirements.txt", f"{local_dir}/requirements.txt")

print("✅ Files prepared")

# Step 2: Upload to Databricks workspace
print("📤 Step 2/4: Uploading to Databricks workspace...")
# Use databricks CLI or SDK to upload
os.system(f"databricks workspace import-dir {local_dir} {WORKSPACE_PATH} --overwrite")

print("✅ Files uploaded")

# Step 3: Deploy app
print("🚢 Step 3/4: Deploying app...")
os.system(f"databricks apps deploy payment-authorization-premium --source-code-path {WORKSPACE_PATH}")

print("✅ App deployed")

# Step 4: Get app URL
print("🔗 Step 4/4: Getting app URL...")
result = os.popen("databricks apps get payment-authorization-premium").read()
print(result)

print("\n🎉 Deployment complete! Access your app at the URL above.")
```

Run with:
```bash
python deploy_premium_app.py
```

---

## 📋 Pre-Deployment Checklist

### Required Files
- [x] `app.py` (renamed from `08_premium_app_ui.py`)
- [x] `app.yaml` (from root directory)
- [x] `requirements.txt` (from root directory)

### Required Permissions
- [x] Workspace CREATE permission
- [x] Apps DEPLOY permission
- [x] Unity Catalog READ access (for `payments_lakehouse`)

### Required Infrastructure
- [x] Unity Catalog: `payments_lakehouse`
- [x] Schemas: `bronze`, `silver`, `gold`
- [x] Tables: Run notebooks 01-05 first to create data

---

## 🔍 Verification Steps

### 1. Check File Structure in Workspace
```
/Workspace/Users/<your-email>/payment-authorization-premium/
├── app.py                ✅ (62 KB, renamed from 08_premium_app_ui.py)
├── app.yaml              ✅ (7.5 KB)
└── requirements.txt      ✅ (4.7 KB)
```

### 2. Verify App Deployment
```bash
# Check app status
databricks apps get payment-authorization-premium

# Expected output:
# Name: payment-authorization-premium
# Status: RUNNING
# URL: https://<workspace>.cloud.databricks.com/apps/<app-id>
```

### 3. Test App Functionality
1. Open app URL
2. Check all 8 pages load:
   - 🏠 Executive Dashboard
   - 🗺️ Global Geo-Analytics
   - 🎯 Smart Checkout
   - 📉 Decline Analysis
   - 🔄 Smart Retry
   - 📊 Performance Metrics
   - 🤖 Genie AI Assistant
   - ⚙️ Settings & Config
3. Verify maps render (PyDeck bubble map, choropleth)
4. Test country drill-down in Geo-Analytics
5. Check sidebar navigation

---

## 🐛 Troubleshooting

### Issue 1: "No command to run" Error
**Cause:** `app.yaml` missing or incorrect command path

**Fix:**
```yaml
# Ensure app.yaml has this:
command: ['streamlit', 'run', 'app.py', '--server.port=8501', '--server.address=0.0.0.0']
```

### Issue 2: "Module not found" Error
**Cause:** Missing dependencies in requirements.txt

**Fix:** Ensure `requirements.txt` includes:
```
streamlit==1.29.0
plotly==5.18.0
pydeck==0.8.1b0
streamlit-extras==0.3.6
streamlit-option-menu==0.3.6
```

### Issue 3: "Table not found" Error
**Cause:** Unity Catalog tables don't exist

**Fix:** Run data generation notebooks first:
```bash
# In Databricks, run these notebooks in order:
1. 00_deployment_setup.py
2. 01_ingest_synthetic_data.py
3. 02_stream_enrichment_smart_checkout.py
4. 03_reason_code_performance.py
5. 04_smart_retry.py
```

### Issue 4: Maps Not Rendering
**Cause:** PyDeck or Plotly not installed

**Fix:**
```bash
# Add to requirements.txt:
pydeck==0.8.1b0
plotly==5.18.0
```

### Issue 5: App Crashes on Startup
**Cause:** Incompatible Streamlit version

**Fix:**
```bash
# Pin exact versions in requirements.txt:
streamlit==1.29.0  # Not 1.30+
```

---

## 🎉 Success Indicators

✅ App status shows `RUNNING`  
✅ All 8 pages load without errors  
✅ Maps render (bubble map + choropleth)  
✅ Country drill-down works  
✅ Charts display data  
✅ KPI cards show metrics  
✅ Sidebar navigation functions  
✅ Genie AI responds to queries  

---

## 📞 Need Help?

1. **Check app logs:**
   ```bash
   databricks apps logs payment-authorization-premium
   ```

2. **Verify Unity Catalog access:**
   ```sql
   USE CATALOG payments_lakehouse;
   SHOW SCHEMAS;
   SHOW TABLES IN silver;
   ```

3. **Test locally (with limitations):**
   ```bash
   cd /Users/ariel.hdez/Downloads/solutions/accelerate_approvals_demo/notebooks/08_premium_app
   streamlit run 08_premium_app_ui.py
   ```
   Note: Will use synthetic data, not real Unity Catalog tables

---

## 🎯 Next Steps After Deployment

1. **Customize branding:** Update logo URL in app code
2. **Add users:** Configure RBAC in Databricks Apps settings
3. **Set up monitoring:** Enable app analytics and logging
4. **Configure alerts:** Set up notifications for app errors
5. **Schedule refreshes:** Automate data updates with Databricks Workflows
6. **Share URL:** Distribute app URL to stakeholders

---

**Deployment Time:** 5-10 minutes  
**App Size:** 62 KB  
**Dependencies:** 9 packages  
**Data Requirements:** Unity Catalog with `payments_lakehouse`  
**Status:** ✅ Ready for Production
