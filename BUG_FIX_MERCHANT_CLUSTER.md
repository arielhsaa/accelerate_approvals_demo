# Bug Fix: Merchant Cluster Column Aliasing Issue

## 🐛 Bug Description

**Issue:** The `merchant_cluster` column was incorrectly aliased as `merchant_category` in dashboard views, causing misleading data representation.

**Impact:** High - Dashboard consumers expecting business categories (like "Retail", "E-commerce") would receive risk classification values (like "low_risk", "medium_risk", "high_risk") instead.

---

## 🔍 Root Cause Analysis

### What is `merchant_cluster`?
The `merchant_cluster` column in the `merchants_dim` table contains **risk classification values**:
- `"low_risk"`
- `"medium_risk"`
- `"high_risk"`

These values are derived from merchant risk scores and represent risk levels, NOT business categories.

### The Problem
In multiple dashboard queries, `merchant_cluster` was aliased as `merchant_category`:

```sql
-- ❌ INCORRECT (Before fix)
m.merchant_cluster AS merchant_category
```

This caused:
1. **Semantic confusion**: Users expected business categories but got risk levels
2. **Misleading visualizations**: Charts labeled "merchant_category" showed risk classifications
3. **Integration issues**: Downstream consumers expecting categorical data received risk scores
4. **Data quality concerns**: Field names didn't match their actual content

---

## ✅ Fixes Applied

### File 1: `dashboards/01_risk_scoring_by_sector.sql`

**Location:** Query 4 - High-Risk Industry Spotlight (Lines 132-159)

**Before:**
```sql
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_high_risk_industries AS
SELECT 
  m.mcc_description AS merchant_sector,
  m.merchant_cluster AS merchant_category,  -- ❌ MISLEADING
  m.mcc AS mcc_code,
  ...
```

**After:**
```sql
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_high_risk_industries AS
SELECT 
  m.mcc_description AS merchant_sector,
  m.merchant_cluster AS merchant_risk_cluster,  -- ✅ ACCURATE
  m.mcc AS mcc_code,
  ...
```

**Impact:**
- View: `payments_lakehouse.gold.dashboard_high_risk_industries`
- Column renamed: `merchant_category` → `merchant_risk_cluster`
- Affected rows: Up to 50 high-risk industries

---

### File 2: `dashboards/03_standard_vs_optimized_approval_rates.sql`

**Location:** Query 2 - Approval Rate Uplift by Segment (Lines 99-124)

**Before:**
```sql
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_uplift_by_segment AS
WITH segmented_performance AS (
  SELECT 
    t.cardholder_country AS geography,
    t.channel,
    t.merchant_cluster AS merchant_category,  -- ❌ MISLEADING
    CASE 
      WHEN t.amount < 50 THEN '0-50'
      ...
```

**After:**
```sql
CREATE OR REPLACE VIEW payments_lakehouse.gold.dashboard_uplift_by_segment AS
WITH segmented_performance AS (
  SELECT 
    t.cardholder_country AS geography,
    t.channel,
    t.merchant_cluster AS merchant_risk_cluster,  -- ✅ ACCURATE
    CASE 
      WHEN t.amount < 50 THEN '0-50'
      ...
```

**Impact:**
- View: `payments_lakehouse.gold.dashboard_uplift_by_segment`
- Column renamed in CTE: `merchant_category` → `merchant_risk_cluster`
- Affects segmented performance analysis

---

## 📊 Verification

### Files Checked
- ✅ `dashboards/01_risk_scoring_by_sector.sql` - **Fixed (1 instance)**
- ✅ `dashboards/02_transactions_by_country.sql` - No issues found
- ✅ `dashboards/03_standard_vs_optimized_approval_rates.sql` - **Fixed (1 instance)**
- ✅ `resources/sql/dashboard_views.sql` - No issues found
- ✅ `notebooks/05_dashboards_and_genie_examples.sql` - No issues found
- ✅ All Python files (`.py`) - No issues found

### Total Fixes
- **2 files modified**
- **2 column aliases corrected**
- **0 semantic ambiguities remaining**

---

## 🎯 New Column Naming Convention

To prevent similar issues in the future:

### Use `merchant_cluster` or `merchant_risk_cluster` for:
- Risk classification values ("low_risk", "medium_risk", "high_risk")
- Risk-based merchant segmentation
- Derived from merchant risk scores

### Use `merchant_category` for:
- Business categories (e.g., "Retail", "E-commerce", "Travel")
- Industry classifications
- Actual merchant type/vertical

### Correct Examples:
```sql
-- ✅ For risk levels
m.merchant_cluster AS merchant_risk_cluster

-- ✅ If you had actual business categories (not in current schema)
m.business_category AS merchant_category

-- ✅ For MCC descriptions (actual business info)
m.mcc_description AS merchant_sector
```

---

## 🔄 Downstream Impact

### Who Needs to Update?

1. **Dashboard Consumers:**
   - Views now return `merchant_risk_cluster` instead of `merchant_category`
   - Update any queries or reports referencing `merchant_category`

2. **Visualizations:**
   - Update chart labels from "Merchant Category" to "Merchant Risk Cluster"
   - Update tooltips and legends accordingly

3. **Documentation:**
   - Data dictionaries should reflect the corrected column names
   - Dashboard user guides should be updated

### Migration Query

If you have saved queries or reports using the old column name:

```sql
-- Old query (will fail after fix)
SELECT merchant_category, COUNT(*) 
FROM payments_lakehouse.gold.dashboard_high_risk_industries
GROUP BY merchant_category;

-- New query (correct)
SELECT merchant_risk_cluster, COUNT(*) 
FROM payments_lakehouse.gold.dashboard_high_risk_industries
GROUP BY merchant_risk_cluster;
```

---

## ✅ Testing Performed

### 1. Syntax Validation
```bash
# All SQL files validated successfully
✅ dashboards/01_risk_scoring_by_sector.sql - Valid SQL syntax
✅ dashboards/03_standard_vs_optimized_approval_rates.sql - Valid SQL syntax
```

### 2. Semantic Verification
- ✅ Column names now accurately represent their content
- ✅ No more ambiguous aliases
- ✅ Consistent naming across all dashboard queries

### 3. Grep Search
```bash
# Confirmed no remaining instances
grep -r "merchant_cluster AS merchant_category" dashboards/
# Result: 0 matches
```

---

## 📝 Summary

### What Changed
- `merchant_category` → `merchant_risk_cluster` (2 views affected)

### Why It Matters
- Prevents data misinterpretation
- Ensures semantic accuracy
- Improves data quality and trust
- Aligns column names with actual content

### Action Required
- Redeploy affected dashboard views
- Update any dependent queries/reports
- Communicate changes to dashboard users

---

## 🚀 Deployment

To apply these fixes in Databricks:

```sql
-- Run the updated SQL files to recreate the views
%run /Workspace/Users/<your-email>/payment-authorization/dashboards/01_risk_scoring_by_sector.sql
%run /Workspace/Users/<your-email>/payment-authorization/dashboards/03_standard_vs_optimized_approval_rates.sql

-- Verify the changes
DESCRIBE payments_lakehouse.gold.dashboard_high_risk_industries;
DESCRIBE payments_lakehouse.gold.dashboard_uplift_by_segment;

-- Expected: Column name should be 'merchant_risk_cluster' not 'merchant_category'
```

---

*Bug Report Date: 2026-01-31*  
*Fixed By: Automated code review and correction*  
*Status: ✅ RESOLVED*  
*Files Modified: 2*  
*Lines Changed: 2*
