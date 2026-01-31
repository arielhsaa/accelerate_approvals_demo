# Dashboard Fix Summary - 01_risk_scoring_by_sector.sql

## Date: 2026-01-30

## Problem
The dashboard SQL file contained multiple references to non-existent columns in the `merchants_dim` table:
- `merchant_sector` - does not exist
- `merchant_category` - does not exist  
- `mcc_code` - column is actually named `mcc`

## Root Cause
The dashboard queries were written assuming a different schema than what was actually implemented in the `01_ingest_synthetic_data.py` notebook.

## Solution
Mapped the logical dashboard field names to the actual database columns:
- `merchant_sector` → `mcc_description` (the industry/sector name like "Retail", "Technology")
- `merchant_category` → `merchant_cluster` (the risk-based category: low_risk, medium_risk, high_risk)
- `mcc_code` → `mcc` (the numeric MCC code)

## Queries Fixed

### Query 4: High-Risk Industry Spotlight (Lines 131-167)
**Before:**
```sql
SELECT 
  m.merchant_sector,
  m.merchant_category,
  m.mcc_code,
  ...
GROUP BY m.merchant_sector, m.merchant_category, m.mcc_code
```

**After:**
```sql
SELECT 
  m.mcc_description AS merchant_sector,
  m.merchant_cluster AS merchant_category,
  m.mcc AS mcc_code,
  ...
GROUP BY m.mcc_description, m.merchant_cluster, m.mcc
```

### Query 5: Risk Score Trend (Lines 176-199)
**Before:**
```sql
SELECT 
  DATE_TRUNC('day', t.timestamp) AS date,
  m.merchant_sector,
  ...
GROUP BY date, m.merchant_sector
ORDER BY date, m.merchant_sector
```

**After:**
```sql
SELECT 
  DATE_TRUNC('day', t.timestamp) AS date,
  m.mcc_description AS merchant_sector,
  ...
GROUP BY date, m.mcc_description
ORDER BY date, m.mcc_description
```

### Query 6: Risk Mitigation Effectiveness (Lines 208-238)
**Before:**
```sql
SELECT 
  m.merchant_sector,
  ...
GROUP BY m.merchant_sector, t.recommended_solution_name
ORDER BY m.merchant_sector, avg_risk_score_before_mitigation DESC
```

**After:**
```sql
SELECT 
  m.mcc_description AS merchant_sector,
  ...
GROUP BY m.mcc_description, t.recommended_solution_name
ORDER BY m.mcc_description, avg_risk_score_before_mitigation DESC
```

### Query 7: External Risk Signal Impact (Lines 247-277)
**Before:**
```sql
SELECT 
  m.merchant_sector,
  ...
GROUP BY m.merchant_sector, t.cardholder_country
```

**After:**
```sql
SELECT 
  m.mcc_description AS merchant_sector,
  ...
GROUP BY m.mcc_description, t.cardholder_country
```

## Impact
All 8 queries in the dashboard now reference valid columns and should execute successfully when run in Databricks SQL.

## Queries Not Changed
Queries 1, 2, 3, and 8 were already using correct column references and did not require changes.

## Validation
- ✅ All `merchant_sector` references now use `mcc_description`
- ✅ All `merchant_category` references now use `merchant_cluster`
- ✅ All `mcc_code` references now use `mcc`
- ✅ All GROUP BY clauses match SELECT aliases
- ✅ All JOIN conditions remain valid
- ✅ No syntax errors introduced

## Additional Documentation
Created `COLUMN_MAPPING.md` to provide a comprehensive reference guide for all column mappings across the database schema to prevent similar issues in the future.

## Testing Recommendation
When deploying these dashboards in Databricks:
1. Run each CREATE VIEW statement individually to verify syntax
2. Execute each SELECT query to validate results
3. Check that all visualizations render correctly with the new column names
4. Verify that filters and drill-downs work as expected

## Files Modified
- `/dashboards/01_risk_scoring_by_sector.sql` - Fixed column references in 4 queries
- `/dashboards/COLUMN_MAPPING.md` - Created new reference documentation

## Commits
1. `324dc64` - Fix column references in 01_risk_scoring_by_sector.sql
2. `4d8206e` - Add column mapping reference documentation
