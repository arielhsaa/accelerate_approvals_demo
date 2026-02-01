#!/bin/bash

# Databricks App Diagnostic Script
# Run this to diagnose why you're still getting 502 errors

set -e

echo "============================================================================"
echo "DATABRICKS APP DIAGNOSTIC - Finding the 502 Error Root Cause"
echo "============================================================================"
echo ""

# Configuration
export USER_EMAIL="ariel.hdez@databricks.com"
export APP_NAME="payment-authorization-premium"
export APP_PATH="/Workspace/Users/$USER_EMAIL/$APP_NAME"

echo "Configuration:"
echo "  User: $USER_EMAIL"
echo "  App: $APP_NAME"
echo "  Path: $APP_PATH"
echo ""

# Test 1: Check if files exist
echo "============================================================================"
echo "TEST 1: Checking if files are uploaded to Databricks..."
echo "============================================================================"
echo ""

echo "Files in $APP_PATH:"
databricks workspace ls "$APP_PATH/" || echo "❌ ERROR: Directory doesn't exist or is empty!"
echo ""

# Test 2: Check if app.py is the NEW version (no @st.cache_data)
echo "============================================================================"
echo "TEST 2: Checking if app.py is the FIXED version..."
echo "============================================================================"
echo ""

echo "Searching for @st.cache_data decorators (should find NONE):"
databricks workspace export "$APP_PATH/app.py" 2>/dev/null | grep -n "@st.cache_data" && echo "❌ FOUND OLD FILE!" || echo "✅ GOOD: No @st.cache_data found (fixed version)"
echo ""

# Test 3: Check app status
echo "============================================================================"
echo "TEST 3: Checking app status..."
echo "============================================================================"
echo ""

databricks apps get "$APP_NAME" 2>&1 || echo "❌ ERROR: App doesn't exist or cannot be accessed"
echo ""

# Test 4: Check recent logs for errors
echo "============================================================================"
echo "TEST 4: Checking logs for errors..."
echo "============================================================================"
echo ""

echo "Last 50 lines of logs:"
echo "---"
databricks apps logs "$APP_NAME" 2>&1 | tail -50 || echo "❌ ERROR: Cannot get logs"
echo "---"
echo ""

echo "Searching for errors in logs:"
databricks apps logs "$APP_NAME" 2>&1 | grep -i "error\|exception\|failed\|traceback" | tail -20 || echo "✅ No obvious errors in logs"
echo ""

# Test 5: Check if app.yaml is new version
echo "============================================================================"
echo "TEST 5: Checking if app.yaml has optimized settings..."
echo "============================================================================"
echo ""

echo "Checking initialDelaySeconds (should be 300):"
databricks workspace export "$APP_PATH/app.yaml" 2>/dev/null | grep "initialDelaySeconds" || echo "❌ Cannot check app.yaml"
echo ""

# Summary
echo "============================================================================"
echo "DIAGNOSTIC SUMMARY"
echo "============================================================================"
echo ""
echo "Next steps based on results above:"
echo ""
echo "1. If files are MISSING or OLD:"
echo "   → Upload the fixed files (see commands below)"
echo ""
echo "2. If logs show dependency errors:"
echo "   → Try the ultra-minimal test app"
echo ""
echo "3. If app status shows ERROR:"
echo "   → Check the error_message field"
echo ""
echo "4. If everything looks OK but still 502:"
echo "   → Try force clean redeploy (see STILL_502_DIAGNOSTIC.md)"
echo ""
echo "============================================================================"
echo "QUICK FIX COMMANDS"
echo "============================================================================"
echo ""
echo "# Upload fixed files:"
echo "databricks workspace upload app.py $APP_PATH/app.py --overwrite"
echo "databricks workspace upload app.yaml $APP_PATH/app.yaml --overwrite"
echo "databricks workspace upload requirements.txt $APP_PATH/requirements.txt --overwrite"
echo ""
echo "# Redeploy:"
echo "databricks apps deploy $APP_NAME --source-code-path $APP_PATH"
echo ""
echo "# Monitor logs:"
echo "databricks apps logs $APP_NAME --follow"
echo ""
echo "============================================================================"
echo "DIAGNOSTIC COMPLETE"
echo "============================================================================"
