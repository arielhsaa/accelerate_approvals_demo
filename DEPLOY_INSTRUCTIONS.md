# Databricks App Deployment Instructions

## ❌ Error: "File does not exist: app.py"

This error means the deployment is looking in a Databricks Workspace path, but the files aren't uploaded there yet.

---

## 🔧 Solution: Upload Files to Databricks Workspace First

You have **two options** to deploy:

---

## Option 1: Upload via Databricks UI (Recommended)

### Step 1: Upload Files to Workspace

1. Open your Databricks workspace in a browser
2. Navigate to **Workspace** → **Users** → **[your-email]**
3. Right-click and select **Create** → **Folder**
4. Name it: `payment-authorization-premium`
5. Click into the new folder
6. Click **Upload** button (top-right)
7. Upload these 3 files from your local machine:
   - `app.py` (60 KB)
   - `app.yaml` (5.5 KB)
   - `requirements.txt` (1.4 KB)

### Step 2: Deploy via CLI

Now that files are in Workspace, run:

```bash
databricks apps deploy payment-authorization-premium \
  --source-code-path /Workspace/Users/ariel.hdez@databricks.com/payment-authorization-premium
```

**Note:** Replace `ariel.hdez@databricks.com` with your actual Databricks email.

---

## Option 2: Use Git Integration (Alternative)

### Step 1: Add Databricks Git Repo

1. In Databricks UI, go to **Repos**
2. Click **Add Repo**
3. Enter your GitHub URL: `https://github.com/arielhsaa/accelerate_approvals_demo.git`
4. Clone the repo to Databricks

### Step 2: Deploy from Repo

```bash
databricks apps deploy payment-authorization-premium \
  --source-code-path /Repos/[your-user]/accelerate_approvals_demo
```

---

## Option 3: Deploy via Databricks UI (No CLI)

### Complete UI-Based Deployment

1. **Navigate to Apps:**
   - In Databricks workspace, click **Apps** in the left sidebar

2. **Create New App:**
   - Click **Create App** button

3. **Configure App:**
   - **Name:** `payment-authorization-premium`
   - **Source:** Upload files or select from Workspace/Repos
   - Upload the 3 files (app.py, app.yaml, requirements.txt)

4. **Deploy:**
   - Click **Deploy** button
   - Wait for deployment to complete (3-5 minutes)

5. **Access App:**
   - Once deployed, click **Open App**
   - URL will be: `https://[workspace-url]/apps/payment-authorization-premium`

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- ✅ Files exist in Databricks Workspace (not just local machine)
- ✅ Path in deployment command matches actual Workspace location
- ✅ You have correct permissions to create apps
- ✅ Databricks CLI is authenticated:
  ```bash
  databricks auth login --host https://[your-workspace-url]
  ```

---

## 🔍 Verify Files in Workspace

To check if files are uploaded correctly:

```bash
# List files in workspace directory
databricks workspace ls /Workspace/Users/ariel.hdez@databricks.com/payment-authorization-premium

# Expected output:
# app.py
# app.yaml
# requirements.txt
```

---

## 🐛 Troubleshooting

### Error: "File does not exist"
**Cause:** Files not uploaded to Databricks Workspace  
**Solution:** Upload files first (see Option 1 Step 1)

### Error: "Permission denied"
**Cause:** Insufficient workspace permissions  
**Solution:** Contact your workspace admin for Apps creation permission

### Error: "Invalid app.yaml"
**Cause:** YAML syntax issue  
**Solution:** Files are already validated, re-upload app.yaml

### Error: "Module not found"
**Cause:** Missing dependencies  
**Solution:** Check requirements.txt is uploaded and contains all packages

---

## 📦 Quick Upload Script

Save this as `upload_to_databricks.sh`:

```bash
#!/bin/bash

# Configuration
WORKSPACE_URL="https://your-workspace.databricks.com"
USER_EMAIL="ariel.hdez@databricks.com"
WORKSPACE_PATH="/Workspace/Users/${USER_EMAIL}/payment-authorization-premium"

# Upload files
echo "Uploading app files to Databricks..."

databricks workspace upload app.py "${WORKSPACE_PATH}/app.py" --overwrite
databricks workspace upload app.yaml "${WORKSPACE_PATH}/app.yaml" --overwrite
databricks workspace upload requirements.txt "${WORKSPACE_PATH}/requirements.txt" --overwrite

echo "✅ Files uploaded successfully!"
echo ""
echo "Now run:"
echo "databricks apps deploy payment-authorization-premium --source-code-path ${WORKSPACE_PATH}"
```

Make executable and run:
```bash
chmod +x upload_to_databricks.sh
./upload_to_databricks.sh
```

---

## 🎯 Complete Deployment Flow

```
1. Local Files (your machine)
   ├── app.py
   ├── app.yaml
   └── requirements.txt
          ↓
2. Upload to Databricks Workspace
   → /Workspace/Users/[email]/payment-authorization-premium/
          ↓
3. Deploy App
   → databricks apps deploy ...
          ↓
4. App Running
   → https://[workspace]/apps/payment-authorization-premium
```

---

## 📞 Need Help?

If you continue to have issues:

1. **Verify authentication:**
   ```bash
   databricks current-user me
   ```

2. **Check workspace path:**
   ```bash
   databricks workspace ls /Workspace/Users/
   ```

3. **View app logs:**
   ```bash
   databricks apps logs payment-authorization-premium
   ```

---

*Last Updated: 2026-01-31*
*Next Step: Upload files to Databricks Workspace first!*
