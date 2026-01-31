# 🔴 Troubleshooting: 502 Bad Gateway Error

## What This Error Means

**502 Bad Gateway** indicates that:
- ✅ Your app deployment succeeded
- ✅ The Databricks gateway received your request
- ❌ The gateway cannot connect to your app (the app isn't responding properly)

This is different from "App Not Available" - your app **started** but isn't responding correctly.

---

## 🔍 Immediate Diagnostic Steps

### Step 1: Check App Status (30 seconds)

```bash
databricks apps get payment-authorization-premium
```

Look for the `"state"` field:
- `"STARTING"` → **Wait 2-3 more minutes** (app still initializing)
- `"RUNNING"` → **App is up but not responding** (check logs)
- `"FAILED"` → **Critical error** (check logs immediately)
- `"UNHEALTHY"` → **Health check failing** (common cause of 502)

---

### Step 2: Check Logs (CRITICAL)

```bash
# Get last 100 lines
databricks apps logs payment-authorization-premium --tail 100

# Or follow in real-time
databricks apps logs payment-authorization-premium --follow
```

**Look for these specific patterns:**

#### Pattern 1: Health Check Failures (Most Common)
```
Health check failed: Connection refused
Health check failed: Timeout waiting for /_stcore/health
```
**Meaning:** Streamlit isn't fully started yet or crashed

#### Pattern 2: Port Binding Issues
```
Error: Address already in use
OSError: [Errno 98] Address already in use
```
**Meaning:** Port 8501 conflict (rare in Databricks)

#### Pattern 3: Streamlit Startup Errors
```
ModuleNotFoundError: No module named 'X'
ImportError: cannot import name 'Y'
```
**Meaning:** Missing dependency or import error

#### Pattern 4: App Running But Not Ready
```
You can now view your Streamlit app in your browser.
Network URL: http://0.0.0.0:8501
```
**Meaning:** Streamlit started but might still be loading data

---

## 🎯 Most Likely Causes (Ranked)

### 1. ⏳ **App Still Starting** (50% probability)

**Symptoms:**
- Just deployed or restarted
- Logs show "Installing dependencies..."
- State is `STARTING` or just changed to `RUNNING`

**Solution:**
```bash
# Wait and check status every 30 seconds
watch -n 30 "databricks apps get payment-authorization-premium | grep state"

# Typical startup time: 2-4 minutes
# With dependencies: 3-5 minutes
```

**Action:** Wait 5 minutes total before investigating further

---

### 2. 🏥 **Health Check Timing Out** (30% probability)

**Symptoms:**
- App state is `UNHEALTHY`
- Logs show health check failures
- Streamlit started but not responding to `/_stcore/health`

**Diagnosis:**
```bash
# Check health check config
grep -A 5 "healthCheck:" app.yaml
```

**Current Settings:**
```yaml
initialDelaySeconds: 120    # 2 minutes
periodSeconds: 15           # Check every 15 seconds
timeoutSeconds: 10          # 10 second timeout
failureThreshold: 5         # 5 failures before marking unhealthy
```

**Solutions:**

A. **Increase timeouts:**
```yaml
healthCheck:
  initialDelaySeconds: 180   # Increase to 3 minutes
  periodSeconds: 20          # Check less frequently
  timeoutSeconds: 15         # Longer timeout
  failureThreshold: 10       # More tolerance
```

B. **Check if Streamlit is actually running:**
```bash
# Look for this in logs
databricks apps logs payment-authorization-premium | grep "You can now view"
```

---

### 3. 💥 **App Crashed After Starting** (15% probability)

**Symptoms:**
- Logs show Streamlit started
- Then errors appear
- App restarts repeatedly

**Common Crash Causes:**

A. **Runtime Error in app.py:**
```python
# Example errors
NameError: name 'spark' is not defined
AttributeError: 'NoneType' object has no attribute 'X'
KeyError: 'column_name'
```

**Solution:** Check logs for Python traceback, fix error in app.py

B. **Memory/Resource Issues:**
```
OOMKilled: Container was killed due to out-of-memory
```

**Solution:** Increase memory in app.yaml:
```yaml
resources:
  limits:
    memory: "32Gi"    # Increase from 16Gi
```

---

### 4. 🔌 **Port Mismatch** (5% probability)

**Symptoms:**
- Health check points to wrong port
- Streamlit starts on different port than configured

**Diagnosis:**
```bash
# Verify port consistency
grep -E "port|8501" app.yaml
```

**Should see:**
```yaml
command:
  - '--server.port=8501'
healthCheck:
  port: 8501
env:
  - name: 'STREAMLIT_SERVER_PORT'
    value: '8501'
```

**Solution:** Ensure all port references are `8501`

---

## 🔧 Quick Fixes

### Fix 1: Restart the App

```bash
# Sometimes a simple restart helps
databricks apps stop payment-authorization-premium
databricks apps start payment-authorization-premium

# Or redeploy
databricks apps deploy payment-authorization-premium \
  --source-code-path /Workspace/Users/[email]/payment-authorization-premium
```

### Fix 2: Increase Health Check Tolerance

Update `app.yaml`:
```yaml
healthCheck:
  path: "/_stcore/health"
  port: 8501
  initialDelaySeconds: 180   # 3 minutes
  periodSeconds: 20
  timeoutSeconds: 15
  failureThreshold: 10       # Very tolerant
```

Then redeploy.

### Fix 3: Check Resource Usage

```bash
# If app keeps crashing, might need more resources
# Increase memory/CPU in app.yaml
```

---

## 📊 Diagnostic Command Suite

Run these commands to get full picture:

```bash
# 1. App status
echo "=== APP STATUS ===="
databricks apps get payment-authorization-premium

# 2. Last 200 log lines
echo -e "\n=== LAST 200 LOG LINES ===="
databricks apps logs payment-authorization-premium --tail 200

# 3. Check for Streamlit startup message
echo -e "\n=== STREAMLIT STARTUP ===="
databricks apps logs payment-authorization-premium | grep -i "streamlit\|you can now view"

# 4. Check for health check messages
echo -e "\n=== HEALTH CHECK STATUS ===="
databricks apps logs payment-authorization-premium | grep -i "health"

# 5. Check for errors
echo -e "\n=== ERRORS ===="
databricks apps logs payment-authorization-premium | grep -i "error\|exception\|failed"
```

---

## 🎯 Step-by-Step Troubleshooting

### Step 1: Wait (2 minutes)
```bash
# Just deployed? Wait first
sleep 120
databricks apps get payment-authorization-premium
```

### Step 2: Check State
```bash
STATE=$(databricks apps get payment-authorization-premium | grep '"state"' | cut -d'"' -f4)
echo "App state: $STATE"

# If STARTING → wait more
# If RUNNING → check logs
# If UNHEALTHY → health check failing
# If FAILED → critical error
```

### Step 3: Review Logs
```bash
databricks apps logs payment-authorization-premium --tail 100
```

### Step 4: Look for Specific Issues

**A. Check if Streamlit started:**
```bash
databricks apps logs payment-authorization-premium | grep "You can now view"
```

**B. Check for errors:**
```bash
databricks apps logs payment-authorization-premium | grep -i "error" | tail -20
```

**C. Check health checks:**
```bash
databricks apps logs payment-authorization-premium | grep "health" | tail -20
```

---

## 🆘 Most Common Solution

For 70% of 502 errors, this works:

**Just wait 5 minutes and try again.**

The app is probably:
1. Installing 24 packages from requirements.txt (2-3 minutes)
2. Starting Streamlit (30 seconds)
3. Loading initial data (30 seconds)
4. Waiting for health check to pass (1-2 minutes)

**Total: 4-5 minutes from deployment to fully working**

---

## 📋 What to Share If Still Broken

If error persists after 5 minutes, share:

1. **App Status:**
```bash
databricks apps get payment-authorization-premium
```

2. **Last 200 Log Lines:**
```bash
databricks apps logs payment-authorization-premium --tail 200
```

3. **Health Check Config** (from app.yaml):
```yaml
healthCheck:
  path: "/_stcore/health"
  port: 8501
  initialDelaySeconds: 120
  ...
```

---

## 🔑 Key Indicators

**App is healthy when you see:**
```
✅ State: RUNNING
✅ Logs: "You can now view your Streamlit app"
✅ Logs: "Health check passed"
✅ No recent errors in logs
```

**App has issues when:**
```
❌ State: UNHEALTHY or FAILED
❌ Logs: "Health check failed"
❌ Logs: Python errors/exceptions
❌ Logs: "OOMKilled" or resource errors
```

---

## 🚀 Quick Test

After making any fix:

```bash
# 1. Redeploy
databricks apps deploy payment-authorization-premium \
  --source-code-path /Workspace/Users/[email]/payment-authorization-premium

# 2. Wait 3 minutes
sleep 180

# 3. Check status
databricks apps get payment-authorization-premium

# 4. Try accessing
# If still 502, check logs:
databricks apps logs payment-authorization-premium --tail 100
```

---

**Next Step:** Run the diagnostic commands above and share the output! 🔍

*Last Updated: 2026-01-31*
*502 Error Troubleshooting Guide*
