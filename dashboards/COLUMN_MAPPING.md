# Dashboard Column Mapping Reference

This document provides a reference for column mappings between the logical dashboard schema and the actual database schema.

## Merchants Dimension Table Schema

**Table:** `payments_lakehouse.bronze.merchants_dim`

**Actual Columns:**
- `merchant_id` - Unique merchant identifier
- `merchant_name` - Merchant business name
- `mcc` - Merchant Category Code (numeric)
- `mcc_description` - Industry/sector name (e.g., "Retail", "Hospitality", "Technology")
- `country` - Merchant country code
- `merchant_size` - Size category (enterprise, smb, startup)
- `merchant_cluster` - Risk-based cluster (low_risk, medium_risk, high_risk)
- `risk_score` - Merchant risk score (0.0-1.0)
- `acquirer` - Payment acquirer name
- `onboarding_date` - Date merchant was onboarded

## Column Mappings for Dashboards

When creating dashboard queries, use these mappings:

| Dashboard Field | Actual Column | Notes |
|----------------|---------------|-------|
| `merchant_sector` | `m.mcc_description` | Industry/sector like "Retail", "Technology" |
| `merchant_category` | `m.merchant_cluster` | Risk category: low_risk, medium_risk, high_risk |
| `mcc_code` | `m.mcc` | Numeric MCC code |
| `merchant_industry` | `m.mcc_description` | Same as merchant_sector |

## Payments Enriched Stream Schema

**Table:** `payments_lakehouse.silver.payments_enriched_stream`

**Key Columns:**
- `transaction_id` - Unique transaction ID
- `cardholder_id` - Cardholder identifier
- `merchant_id` - Merchant identifier (joins to merchants_dim)
- `amount` - Transaction amount
- `currency` - Currency code
- `timestamp` - Transaction timestamp
- `is_approved` - Boolean approval status
- `reason_code` - Decline/approval reason code
- `card_network` - Card network (VISA, MASTERCARD, AMEX, DISCOVER)
- `channel` - Transaction channel (ecommerce, moto, pos, atm)
- `cardholder_country` - Cardholder country code
- `is_cross_border` - Boolean cross-border flag
- `is_high_value` - Boolean high-value transaction flag
- `composite_risk_score` - Combined risk score (0.0-1.0)
- `cardholder_risk_score` - Cardholder-specific risk (0.0-1.0)
- `merchant_risk_score` - Merchant-specific risk (0.0-1.0)
- `country_risk_score` - Country risk from external signals (0.0-1.0)
- `sector_risk_score` - Sector risk from external signals (0.0-1.0)
- `aml_risk_level` - AML risk level (0.0-1.0)
- `recommended_solution_name` - Smart checkout solution name
- `recommended_solution_list` - Array of solution components
- `expected_approval_prob` - Predicted approval probability (0.0-1.0)
- `adjusted_risk_score` - Risk score after solution adjustment
- `solution_cost` - Cost of recommended solution in USD
- `cascading_path` - Fallback routing path
- `retry_attempt_number` - Retry attempt count
- Various velocity and behavior features

## Common Query Patterns

### By Merchant Sector/Industry
```sql
SELECT 
  m.mcc_description AS merchant_sector,
  ...
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
GROUP BY m.mcc_description
```

### By Risk Category
```sql
SELECT 
  m.merchant_cluster AS risk_category,
  ...
FROM payments_lakehouse.silver.payments_enriched_stream t
JOIN payments_lakehouse.bronze.merchants_dim m ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_cluster
```

### Approval Status
```sql
-- Approved transactions
WHERE t.is_approved = TRUE

-- Declined transactions
WHERE NOT t.is_approved
-- or
WHERE t.is_approved = FALSE
```

### Cross-Border Transactions
```sql
WHERE t.is_cross_border = TRUE
```

### High-Risk Transactions
```sql
WHERE t.composite_risk_score > 0.75
```

## Fixes Applied

### 01_risk_scoring_by_sector.sql
- Changed `m.merchant_sector` → `m.mcc_description`
- Changed `m.merchant_category` → `m.merchant_cluster`
- Changed `m.mcc_code` → `m.mcc`
- Applied to Queries 4, 5, 6, and 7

### 02_transactions_by_country.sql
- Changed `t.geography` → `t.cardholder_country`
- Changed `t.cross_border_flag` → `t.is_cross_border`
- Changed `t.approval_status` → `t.is_approved` (boolean)
- Changed `t.risk_score` → `t.composite_risk_score`
- Changed `t.payment_method` → `t.card_network`
- Changed `t.chosen_solution_stack` → `t.recommended_solution_name`

### 03_standard_vs_optimized_approval_rates.sql
- Changed `approval_status = 'approved'` → `is_approved`
- Changed `approval_status = 'declined'` → `NOT is_approved`
- Changed `chosen_solution_stack` → `recommended_solution_name`
- Changed `geography` → `cardholder_country`
- Changed `merchant_category` → `merchant_cluster`
- Changed `risk_score` → `composite_risk_score`
- Changed `predicted_approval_probability` → `expected_approval_prob`
- Replaced `processing_costs` with `solution_cost`

## Validation Checklist

When creating new dashboard queries:
- ✅ Use `m.mcc_description` for industry/sector grouping
- ✅ Use `m.merchant_cluster` for risk-based categorization
- ✅ Use `m.mcc` for MCC code (numeric)
- ✅ Use `t.is_approved` (boolean) instead of `approval_status = 'approved'`
- ✅ Use `t.cardholder_country` instead of `geography`
- ✅ Use `t.composite_risk_score` instead of `risk_score`
- ✅ Use `t.recommended_solution_name` instead of `chosen_solution_stack`
- ✅ Use `t.is_cross_border` (boolean) instead of `cross_border_flag`
- ✅ Use `t.card_network` instead of `payment_method`
- ✅ Use `t.solution_cost` instead of `processing_cost_usd`

## Notes

- All risk scores are on a 0.0-1.0 scale
- Boolean fields should use `TRUE/FALSE` or `IS TRUE/IS FALSE`, not `= 1/= 0`
- Timestamps use `current_timestamp()` for relative date filtering
- Use `DATE_TRUNC('day', timestamp)` for daily aggregations
- Use `DATE_TRUNC('hour', timestamp)` for hourly aggregations
