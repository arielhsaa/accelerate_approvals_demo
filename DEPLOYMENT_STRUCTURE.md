# Databricks App Deployment Structure

This document explains the proper file structure for deploying the Payment Authorization app to Databricks.

## 📁 Required Files

For Databricks Apps deployment, you need these three files in the **same directory**:

```
/Workspace/Users/<your-email>/payment-authorization/
├── app.py              ← Main Streamlit application (required)
├── app.yaml            ← App configuration (required)
└── requirements.txt    ← Python dependencies (required)
```

## 🎯 Current Project Structure

This repository has a different structure for development:

```
/accelerate_approvals_demo/
├── app.yaml                     ← Root deployment config ✓
├── requirements.txt             ← Root dependencies ✓
├── notebooks/
│   ├── 06_demo_app/
│   │   └── 06_app_demo_ui.py   ← Standard app
│   └── 07_advanced_app/
│       └── 07_advanced_app_ui.py  ← Advanced app (RECOMMENDED)
└── [other notebooks...]
```

## 🚀 Deployment Options

### Option 1: Deploy Advanced App (Recommended)

Copy the advanced app to match Databricks Apps structure:

```bash
# 1. In Databricks workspace, create a directory:
/Workspace/Users/<your-email>/payment-authorization/

# 2. Upload these files to that directory:
- notebooks/07_advanced_app/07_advanced_app_ui.py → rename to app.py
- app.yaml
- requirements.txt
```

**Via Databricks UI:**
1. Navigate to Workspace → Users → `<your-email>`
2. Create folder: `payment-authorization`
3. Upload files:
   - `notebooks/07_advanced_app/07_advanced_app_ui.py` (rename to `app.py`)
   - `app.yaml` (from root)
   - `requirements.txt` (from root)
4. Go to **Apps** → **Create App** → Select folder → Deploy

**Via Databricks CLI:**
```bash
# First, prepare deployment directory locally
mkdir -p /tmp/payment-authorization-deploy
cp notebooks/07_advanced_app/07_advanced_app_ui.py /tmp/payment-authorization-deploy/app.py
cp app.yaml /tmp/payment-authorization-deploy/
cp requirements.txt /tmp/payment-authorization-deploy/

# Upload to Databricks workspace
databricks workspace import-dir /tmp/payment-authorization-deploy \
  /Workspace/Users/<your-email>/payment-authorization --overwrite

# Deploy the app
databricks apps deploy payment-authorization \
  --source-code-path /Workspace/Users/<your-email>/payment-authorization
```

### Option 2: Deploy Standard App

Use the same process, but copy `06_demo_app/06_app_demo_ui.py` instead:

```bash
cp notebooks/06_demo_app/06_app_demo_ui.py /tmp/payment-authorization-deploy/app.py
# ... rest same as above
```

## 📝 Key Points

### ✅ DO:
- Keep `app.py`, `app.yaml`, and `requirements.txt` in the **same directory**
- Name your main app file as `app.py` (required by Databricks Apps)
- Test locally first: `streamlit run app.py`
- Verify Unity Catalog access before deployment

### ❌ DON'T:
- Don't use relative paths in `app.yaml` command (already configured correctly)
- Don't deploy without all three required files
- Don't use nested directory structures for the app files
- Don't forget to rename your app file to `app.py`

## 🔍 Verification Checklist

Before deploying, verify:

- [ ] `app.py` exists and runs locally with `streamlit run app.py`
- [ ] `app.yaml` has correct command: `['streamlit', 'run', 'app.py', ...]`
- [ ] `requirements.txt` has all necessary dependencies
- [ ] All three files are in the same Databricks workspace directory
- [ ] Unity Catalog `payments_lakehouse` exists with bronze/silver/gold schemas
- [ ] You have permissions to create Databricks Apps

## 🐛 Troubleshooting

### "No command to run" Error
- **Cause**: `app.yaml` is missing or malformed
- **Solution**: Ensure `app.yaml` exists in same directory as `app.py`

### "Module not found" Error
- **Cause**: Missing dependencies in `requirements.txt`
- **Solution**: Check requirements.txt is complete and properly formatted

### "Table not found" Error
- **Cause**: Unity Catalog tables don't exist
- **Solution**: Run notebooks `01_ingest_*.py` through `04_smart_retry.py` first

### "Permission denied" Error
- **Cause**: Insufficient Unity Catalog permissions
- **Solution**: Request READ permissions on `payments_lakehouse` catalog

## 📚 Related Documentation

- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/)
- [Streamlit on Databricks](https://docs.databricks.com/en/dev-tools/databricks-apps/streamlit.html)
- See `DEPLOYMENT.md` for full step-by-step deployment guide
- See `QUICKSTART.md` for rapid setup instructions

## 🎉 Quick Deploy Script

Use this bash script to prepare deployment package:

```bash
#!/bin/bash
# prepare-deploy.sh

APP_DIR="/tmp/payment-authorization-deploy"
WORKSPACE_EMAIL="your.email@company.com"  # UPDATE THIS

echo "🚀 Preparing Databricks App deployment..."

# Create clean deployment directory
rm -rf $APP_DIR
mkdir -p $APP_DIR

# Copy files and rename
echo "📦 Copying files..."
cp notebooks/07_advanced_app/07_advanced_app_ui.py $APP_DIR/app.py
cp app.yaml $APP_DIR/
cp requirements.txt $APP_DIR/

echo "✅ Files prepared in: $APP_DIR"
echo ""
echo "Next steps:"
echo "1. Upload to Databricks:"
echo "   databricks workspace import-dir $APP_DIR /Workspace/Users/$WORKSPACE_EMAIL/payment-authorization --overwrite"
echo ""
echo "2. Deploy the app:"
echo "   databricks apps deploy payment-authorization --source-code-path /Workspace/Users/$WORKSPACE_EMAIL/payment-authorization"
echo ""
echo "Or use Databricks UI: Apps → Create App → Select folder → Deploy"
```

Make executable and run:
```bash
chmod +x prepare-deploy.sh
./prepare-deploy.sh
```

---

**Last Updated**: 2026-01-31  
**Version**: 1.0.0
