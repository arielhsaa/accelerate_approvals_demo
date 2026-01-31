# 🔴 Troubleshooting: "App Not Available" Error

## Error Message
```
App Not Available
Sorry, the Databricks app you are trying to access is currently unavailable. 
Please try again later.
```

---

## 🔍 Quick Diagnosis Steps

### Step 1: Check App Status (CRITICAL)

```bash
# Check if app is running
databricks apps get payment-authorization-premium

# Expected output if running:
# {
#   "name": "payment-authorization-premium",
#   "state": "RUNNING",    # Should be "RUNNING", not "FAILED" or "STARTING"
#   "url": "...",
#   ...
# }
```

**Possible States:**
- `STARTING` → App is still deploying (wait 3-5 minutes)
- `RUNNING` → App should work (if not, check logs)
- `FAILED` → Deployment failed (check logs immediately)
- `STOPPED` → App was stopped manually

---

### Step 2: View Logs (CRITICAL)

```bash
# View recent logs
databricks apps logs payment-authorization-premium --tail 100

# Or follow logs in real-time
databricks apps logs payment-authorization-premium --follow
```

**What to look for:**
1. **Startup errors**
2. **Import errors** (missing packages)
3. **Database connection errors**
4. **Port binding errors**
5. **Health check failures**

---

## 🐛 Common Causes & Solutions

### 1. ⏳ App Still Starting Up

**Symptom:** App shows "Not Available" immediately after deployment

**Cause:** Databricks Apps take 3-5 minutes to start (install dependencies, start Streamlit)

**Solution:**
```bash
# Wait and check status every 30 seconds
watch -n 30 "databricks apps get payment-authorization-premium | grep state"

# Or check logs to see progress
databricks apps logs payment-authorization-premium --follow
```

**Expected log sequence:**
```
✅ Installing dependencies from requirements.txt...
✅ Installing streamlit==1.29.0
✅ Installing plotly==5.18.0
✅ Installing pydeck==0.8.1b0
...
✅ Starting app with command: ['streamlit', 'run', 'app.py', ...]
✅ Streamlit started on port 8501
✅ Health check passed
```

**Action:** Wait 5 minutes, then try again

---

### 2. 📦 Missing Dependencies

**Symptom:** Logs show `ModuleNotFoundError` or `ImportError`

**Example errors:**
```
ModuleNotFoundError: No module named 'streamlit_option_menu'
ModuleNotFoundError: No module named 'pydeck'
ImportError: cannot import name 'option_menu' from 'streamlit_option_menu'
```

**Solution:**

Check your requirements.txt includes all packages:
```bash
# Verify requirements.txt content
cat requirements.txt | grep -E "(streamlit|plotly|pydeck|pandas|databricks)"
```

**Must have:**
```
streamlit==1.29.0
streamlit-extras==0.3.6
streamlit-option-menu==0.3.6
plotly==5.18.0
pydeck==0.8.1b0
pandas==2.1.4
databricks-sql-connector==3.0.2
```

**Action:** 
1. Update requirements.txt if missing packages
2. Re-upload to Databricks Workspace
3. Redeploy the app

---

### 3. 🗄️ Unity Catalog Connection Issues

**Symptom:** Logs show database/table errors

**Example errors:**
```
Table or view not found: payments_lakehouse.silver.payments_enriched_stream
Schema payments_lakehouse.silver not found
Permission denied: CATALOG payments_lakehouse
```

**Solution A: Verify Unity Catalog exists**
```sql
-- In Databricks SQL editor
SHOW CATALOGS;
-- Should show: payments_lakehouse

SHOW SCHEMAS IN payments_lakehouse;
-- Should show: bronze, silver, gold

SHOW TABLES IN payments_lakehouse.silver;
-- Should show: payments_enriched_stream, etc.
```

**Solution B: Check permissions**
```bash
# You need at least USE and SELECT permissions
databricks unity-catalog permissions get \
  --securable-type catalog \
  --full-name payments_lakehouse
```

**Solution C: Run data ingestion first**

The app expects data to exist. Run notebooks first:
```bash
# Run these notebooks in order:
1. notebooks/01_ingest_synthetic_data.py
2. notebooks/02_stream_enrichment_smart_checkout.py
3. notebooks/03_reason_code_performance.py
4. notebooks/04_smart_retry.py
```

**Action:**
1. Create Unity Catalog if missing
2. Run ingestion notebooks
3. Grant permissions if needed
4. Restart the app

---

### 4. 💥 Python Code Errors

**Symptom:** Logs show Python errors after "Starting app..."

**Example errors:**
```
AttributeError: module 'streamlit' has no attribute 'set_page_config'
NameError: name 'pd' is not defined
KeyError: 'composite_risk_score'
```

**Solution:**

Check logs for the exact error and line number:
```bash
databricks apps logs payment-authorization-premium --tail 200 | grep -A 5 "Error\|Exception\|Traceback"
```

**Common fixes:**
- `st.set_page_config` errors → Must be FIRST Streamlit command
- Import errors → Missing `import` statement
- KeyError → Database schema doesn't match code

**Action:** Fix the error in app.py, re-upload, redeploy

---

### 5. 🏥 Health Check Failing

**Symptom:** Logs show health check failures

**Example errors:**
```
Health check failed: Connection refused on port 8501
Health check failed: Timeout waiting for /_stcore/health
```

**Solution:**

Verify health check configuration in app.yaml:
```yaml
healthCheck:
  path: "/_stcore/health"    # Must be this exact path for Streamlit
  port: 8501                  # Must match server port
  initialDelaySeconds: 60     # Give enough time to start
  timeoutSeconds: 5
```

**If Streamlit isn't starting:**
1. Check logs for Streamlit startup errors
2. Verify port 8501 isn't in command twice
3. Check if command is correct: `['streamlit', 'run', 'app.py', '--server.port=8501', ...]`

**Action:** 
1. Increase `initialDelaySeconds` to 90 if still starting
2. Check Streamlit actually started
3. Test health endpoint manually (if possible)

---

### 6. 💾 Resource Limits Exceeded

**Symptom:** Logs show OOM (Out of Memory) errors or app crashes

**Example errors:**
```
Killed (signal 9)
OOMKilled: Container was killed due to out-of-memory
```

**Solution:**

Increase resources in app.yaml:
```yaml
resources:
  limits:
    memory: "16Gi"      # Increase if OOM
    cpu: "8"            # Increase if slow
  requests:
    memory: "8Gi"
    cpu: "4"
```

**For this app:** 16Gi should be enough, but if using large datasets:
```yaml
resources:
  limits:
    memory: "32Gi"      # For very large datasets
    cpu: "16"           # For high concurrency
```

**Action:** Update resources, re-upload, redeploy

---

### 7. 🔧 Configuration Issues

**Symptom:** App starts but immediately fails

**Check these:**

1. **Command format** (must be list):
```yaml
# ✅ CORRECT
command: ['streamlit', 'run', 'app.py']

# ❌ WRONG
command: "streamlit run app.py"
```

2. **File locations** (all at root):
```
/Workspace/Users/[email]/payment-authorization-premium/
  ├── app.py        ✅
  ├── app.yaml      ✅
  └── requirements.txt  ✅
```

3. **Environment variables** (check in app.yaml):
```yaml
env:
  - name: 'CATALOG'
    value: 'payments_lakehouse'    # Must exist!
```

**Action:** Verify all configuration, re-upload if needed

---

## 🔧 Step-by-Step Troubleshooting Process

### 1. Collect Information
```bash
# Get app status
databricks apps get payment-authorization-premium > app_status.json
cat app_status.json

# Get full logs
databricks apps logs payment-authorization-premium > app_logs.txt
cat app_logs.txt | tail -100
```

### 2. Identify the Issue

Look for these patterns in logs:

**Pattern A: Dependencies**
```
ModuleNotFoundError: No module named 'X'
→ Add package to requirements.txt
```

**Pattern B: Database**
```
Table not found: payments_lakehouse.X.Y
→ Run ingestion notebooks first
```

**Pattern C: Code Error**
```
File "app.py", line 123, in <module>
    some_function()
NameError: name 'some_function' is not defined
→ Fix code error in app.py
```

**Pattern D: Startup**
```
Error: Address already in use
→ Port conflict (rare in Databricks)
```

### 3. Fix and Redeploy

```bash
# 1. Fix the issue locally
# 2. Re-upload files
databricks workspace upload app.py /Workspace/Users/[email]/payment-authorization-premium/app.py --overwrite
databricks workspace upload app.yaml /Workspace/Users/[email]/payment-authorization-premium/app.yaml --overwrite
databricks workspace upload requirements.txt /Workspace/Users/[email]/payment-authorization-premium/requirements.txt --overwrite

# 3. Redeploy
databricks apps deploy payment-authorization-premium \
  --source-code-path /Workspace/Users/[email]/payment-authorization-premium

# 4. Watch logs
databricks apps logs payment-authorization-premium --follow
```

---

## 🎯 Quick Diagnostic Commands

Run these to get full picture:

```bash
# 1. App status
echo "=== APP STATUS ===" && \
databricks apps get payment-authorization-premium

# 2. Recent logs (last 100 lines)
echo -e "\n=== RECENT LOGS ===" && \
databricks apps logs payment-authorization-premium --tail 100

# 3. Check if Unity Catalog exists
echo -e "\n=== UNITY CATALOG CHECK ===" && \
databricks unity-catalog catalogs get --name payments_lakehouse

# 4. List workspace files
echo -e "\n=== WORKSPACE FILES ===" && \
databricks workspace ls /Workspace/Users/[your-email]/payment-authorization-premium
```

---

## 📋 Checklist: Common Issues

**Before asking for help, verify:**

- [ ] App state is `RUNNING` (not `FAILED` or `STARTING`)
- [ ] Waited at least 5 minutes after deployment
- [ ] Checked logs for error messages
- [ ] Unity Catalog `payments_lakehouse` exists
- [ ] Tables in `payments_lakehouse.silver` exist
- [ ] All 3 files (app.py, app.yaml, requirements.txt) uploaded to Workspace
- [ ] requirements.txt includes all packages (especially `streamlit-option-menu`, `pydeck`)
- [ ] No Python syntax errors in app.py
- [ ] Health check path is `/_stcore/health`
- [ ] Command in app.yaml is a list format

---

## 🆘 If Still Not Working

**Provide this information:**

1. **App status output:**
```bash
databricks apps get payment-authorization-premium
```

2. **Last 200 lines of logs:**
```bash
databricks apps logs payment-authorization-premium --tail 200
```

3. **Unity Catalog check:**
```sql
SHOW TABLES IN payments_lakehouse.silver;
```

4. **Files in workspace:**
```bash
databricks workspace ls /Workspace/Users/[email]/payment-authorization-premium -l
```

With this information, we can identify the exact issue!

---

## 🎯 Most Likely Causes (90% of cases)

1. **⏳ App still starting** (30%) → Wait 5 minutes
2. **📦 Missing `streamlit-option-menu`** (25%) → Add to requirements.txt
3. **🗄️ Unity Catalog doesn't exist** (20%) → Create catalog and run ingestion
4. **🏥 Health check timing out** (10%) → Increase initialDelaySeconds
5. **💥 Code error in app.py** (10%) → Check logs for Python errors
6. **Other** (5%)

**Next Step:** Check logs first! 👇

```bash
databricks apps logs payment-authorization-premium --tail 100
```

Share the output and I can pinpoint the exact issue!

---

*Last Updated: 2026-01-31*
*Troubleshooting Guide v1.0*
