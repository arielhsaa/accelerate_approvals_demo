# Demo Script: Payment Authorization Command Center

## Overview

**Duration**: 45 minutes  
**Audience**: Mixed (Executives, Product Managers, Data Scientists, Risk Teams)  
**Objective**: Showcase how Databricks accelerates payment approval rates through Smart Checkout, Reason Code Analytics, and Smart Retry

---

## Pre-Demo Setup (5 minutes before start)

- [ ] All notebooks executed and data populated
- [ ] Databricks App deployed and accessible
- [ ] Screen sharing setup with:
  - Databricks Workspace (notebooks view)
  - Databricks App (Command Center UI)
  - SQL Dashboard (optional)
- [ ] Demo data refreshed (latest timestamp within last hour)

---

## Act 1: Setting the Stage (5 minutes)

### Opening Hook

**"Every declined card transaction is a missed opportunity—for the merchant, the payment provider, and the customer. Today, I'll show you how we're using Azure Databricks to turn those missed opportunities into approved transactions."**

### The Business Problem

**Talking Points**:
- Payment industry sees 15-25% decline rates globally
- $118 billion lost annually to false declines (legitimate transactions incorrectly declined)
- Traditional approach: one-size-fits-all payment routing → suboptimal results
- Our goal: **Maximize approval rates while maintaining security and compliance**

### The Solution Overview

**"We've built an end-to-end payment optimization platform on the Databricks Lakehouse with three core capabilities:"**

1. **Smart Checkout**: AI-powered payment solution selection (50+ combinations evaluated per transaction)
2. **Reason Code Performance**: Real-time decline analytics with actionable insights
3. **Smart Retry**: ML-based retry timing optimization (when and how to retry)

---

## Act 2: Data Foundation (5 minutes)

### Show Bronze Layer (Notebook 01)

**Screen**: Open Notebook 01 in Databricks

**Talking Points**:
- "We start with raw transaction data streaming in from payment gateways (simulated here with synthetic data)."
- "Four key datasets:"
  - **Transactions**: Authorization attempts with solution flags (3DS, Antifraud, etc.)
  - **Cardholders**: Customer profiles with KYC segment and risk scores
  - **Merchants**: Merchant dimension with MCC codes, geography, risk profiles
  - **External Risk Signals**: Moody's-style macro/sector risk data

**Demo Action**:
```python
# Show transaction sample
display(spark.table("payments_lakehouse.bronze.transactions_raw").limit(10))
```

**Key Points**:
- Delta Lake format (ACID, time travel, schema evolution)
- Unity Catalog for governance and lineage
- Streaming ingestion with Structured Streaming (real-time mode)

---

## Act 3: Smart Checkout in Action (10 minutes)

### Show Silver Layer & Smart Checkout (Notebook 02)

**Screen**: Open Notebook 02

**Talking Points**:
- "For every transaction, Smart Checkout evaluates 50+ payment solution combinations."
- "Each combination is scored on three dimensions:"
  1. **Approval Uplift**: Expected increase in approval probability
  2. **Risk Reduction**: Decrease in fraud/AML risk
  3. **Cost**: Transaction fees for solutions

**Demo Action**:
```python
# Show enriched transaction with Smart Checkout decision
display(spark.sql("""
SELECT 
    transaction_id,
    cardholder_country,
    merchant_country,
    amount,
    channel,
    composite_risk_score,
    recommended_solution_name,
    expected_approval_prob,
    approval_uplift_pct,
    adjusted_risk_score,
    cascading_path
FROM payments_lakehouse.silver.payments_enriched_stream
LIMIT 10
"""))
```

**Highlight Example**:
```
Transaction: $250 ecommerce, US cardholder, high-risk merchant
├─ Composite Risk: 0.65 (medium-high)
├─ Recommended Solution: "3DS+Antifraud+NetworkToken"
│   ├─ Expected Approval: 92% (baseline: 85%)
│   ├─ Approval Uplift: +7%
│   ├─ Adjusted Risk: 0.35 (-46% reduction)
│   ├─ Cost: $0.33
├─ Cascading Path: ["NetworkToken+3DS", "3DS+IDPay", ...]
└─ Result: APPROVED ✅
```

**Key Points**:
- Business rules applied (mandatory 3DS in EU, high-risk MCC handling)
- Issuer preferences (VISA prefers NetworkToken)
- Cascading: automatic fallback if primary solution fails

### Show Performance Metrics

**Demo Action**:
```sql
-- Show approval uplift by solution mix
SELECT * FROM payments_lakehouse.gold.v_smart_checkout_solution_performance
ORDER BY avg_uplift_pct DESC;
```

**Talking Points**:
- "On average, +8% approval rate improvement across all solutions"
- "Best performing: NetworkToken+3DS (94% approval rate, +9% uplift)"
- "Cost-optimized: DataShareOnly (low cost, +5% uplift for low-risk transactions)"

---

## Act 4: Reason Code Analytics (8 minutes)

### Show Gold Layer (Notebook 03)

**Screen**: Open Notebook 03 or SQL Dashboard

**Talking Points**:
- "When transactions are declined, we don't just log it—we analyze it."
- "Standardized 12 reason codes with full taxonomy (category, severity, actionability)"
- "Real-time aggregations by issuer, geography, merchant, channel, solution mix"

**Demo Action**:
```sql
-- Show top decline reasons
SELECT * FROM payments_lakehouse.gold.v_top_decline_reasons
LIMIT 10;
```

**Highlight Insight Example**:
```
🎯 Insight: reason_code = 05_DO_NOT_HONOR
├─ Volume: 1,234 declines (18% of total)
├─ Root Causes:
│   └─ Risk scoring threshold too conservative
│   └─ Geographic restrictions
├─ Recommended Actions:
│   └─ Enable 3DS + NetworkToken
│   └─ Contact issuer for whitelist
├─ Estimated Impact: 18% of declines recoverable
```

**Demo Action**:
```sql
-- Show actionable insights
SELECT * FROM payments_lakehouse.gold.v_actionable_insights_summary
WHERE priority = 'High'
LIMIT 5;
```

**Key Points**:
- Insights auto-generated based on decline patterns
- Feedback loop: insights update Smart Checkout configuration
- Reduced time to identify issues from days to minutes

### Show Decline Heatmap

**Demo Action**:
```sql
-- Show issuer vs reason code heatmap
SELECT * FROM payments_lakehouse.gold.decline_heatmap_issuer_reason;
```

**Talking Points**:
- "VISA has elevated 05_DO_NOT_HONOR declines in LATAM → Action: Enable 3DS for LATAM"
- "Mastercard shows 63_SECURITY_VIOLATION spikes → Action: Enhance Antifraud"

---

## Act 5: Smart Retry Optimization (8 minutes)

### Show ML Model (Notebook 04)

**Screen**: Open Notebook 04

**Talking Points**:
- "Not all declined transactions should be retried immediately—or at all."
- "We trained a Gradient Boosted Trees model to predict retry success probability."
- "Key features: time since decline, issuer success rate, reason code, is_salary_day, is_business_hours"

**Demo Action**:
```python
# Show model performance
print(f"Model AUC: {auc:.4f}")
print(f"Model Accuracy: {accuracy:.4f}")

# Show feature importance
display(spark.table("payments_lakehouse.gold.retry_model_feature_importance"))
```

**Key Points**:
- Top features: `hours_since_decline`, `issuer_success_rate_7d`, `is_salary_day`
- Model accuracy: 85%+
- Registered in MLflow Model Registry for versioning and deployment

### Show Retry Recommendations

**Demo Action**:
```sql
-- Show retry action distribution
SELECT * FROM payments_lakehouse.gold.v_retry_recommendation_summary;
```

**Highlight Example**:
```
Declined Transaction: reason_code = 51_INSUFFICIENT_FUNDS
├─ Retry Success Probability: 62%
├─ Action: RETRY_LATER
├─ Suggested Delay: 24 hours (salary day tomorrow)
├─ Reasoning: "Wait for salary day + business hours = high recovery probability"
└─ Expected Value Recovered: $89.99
```

**Demo Action**:
```sql
-- Show value recovery estimate
SELECT * FROM payments_lakehouse.gold.v_retry_value_recovery;
```

**Talking Points**:
- "Smart Retry filters out 60% of wasteful retries (low success probability)"
- "Estimated $X million recovered annually vs $Y million with blind retry"
- "30-70% retry success rate (vs 15-25% industry baseline)"

---

## Act 6: Live Monitoring & Command Center (7 minutes)

### Show Databricks App

**Screen**: Open Databricks App (Notebook 06 or 07 deployed as App)
- **Option A**: Standard app (`06_app_demo_ui.py`) - single-page dashboard
- **Option B**: Advanced app (`07_advanced_app_ui.py`) - multi-page with Genie AI ⭐ RECOMMENDED

**Talking Points**:
- "We've built an interactive Command Center for real-time monitoring and control."
- (If using advanced app) "Navigate through dedicated pages for different analysis views."

### Demo Features

1. **KPI Tiles** (top of page):
   - Approval rate: 92.5% (+7.5% vs baseline)
   - Approved value: $X million
   - Avg risk score: 0.35 (-38% reduction)
   - Total transactions: 50,000+

2. **Live Transaction Feed**:
   - Show recent transactions with solution mix and outcomes
   - Apply filters (channel, network, status)
   - Highlight color-coding (green = approved, red = declined)

3. **Sankey Flow Diagram**:
   - Show transaction flow: Channel → Solution Mix → Outcome
   - "Visualize the journey from entry to decision"

4. **Approval Trends**:
   - Show hourly approval rate over 48 hours
   - "Approval rate improved from 85% to 92% over the past week"

5. **Geographic Performance**:
   - Show map or bar chart of approval rates by country
   - "LATAM improved from 78% to 89% after geo-specific routing"

6. **What-If Analysis** (sidebar):
   - Adjust policy thresholds (min approval prob, max risk, max cost)
   - Show projected impact on approval rate, risk, cost
   - "Test policy changes before deploying to production"

**Key Points**:
- Auto-refresh every 10 seconds
- Role-based access control (executives, ops, risk teams)
- Can be embedded in existing dashboards or portals

---

## Act 7: Business Impact & ROI (5 minutes)

### Show Results Summary

**Talking Points**:

**Financial Impact**:
- "By increasing approval rate from 85% to 92%, we recover **$X million annually**"
- "Smart Retry alone recovers **$Y million** with 60% fewer wasteful attempts"

**Operational Efficiency**:
- "Reason Code Analytics reduced issue resolution time from **days to minutes**"
- "Automated feedback loops eliminate manual policy tuning"

**Customer Experience**:
- "7.5% fewer declined transactions = 7.5% fewer frustrated customers"
- "Smart Retry at optimal timing increases customer trust"

**Risk & Compliance**:
- "38% risk reduction with smart solution stacks"
- "Maintained PSD2 compliance (mandatory 3DS in EU) while maximizing approvals"

### Technical Highlights

**Architecture Benefits**:
- **Lakehouse Architecture**: Unified data platform (no data silos)
- **Real-Time Processing**: Sub-second decision latency with Structured Streaming
- **ML at Scale**: Train on millions of transactions, deploy with MLflow
- **Governance**: Unity Catalog for lineage, access control, audit logs

---

## Act 8: Q&A and Next Steps (5 minutes)

### Common Questions

**Q: How does this integrate with our existing payment gateway?**  
A: "Replace synthetic data ingestion with Event Hubs/Kafka connector to your gateway. The rest of the pipeline is plug-and-play."

**Q: How long does deployment take?**  
A: "Initial setup: 1-2 days. Full production with real data: 2-4 weeks including testing and validation."

**Q: Can we customize the solution mixes and business rules?**  
A: "Absolutely. All configuration is in JSON files (`routing_policies.json`, `retry_policies.json`). Easy to update and version control."

**Q: What about data privacy and compliance?**  
A: "Unity Catalog provides RBAC, PII masking, audit logs. Delta Lake enables GDPR right-to-be-forgotten with time travel."

**Q: How do we monitor model drift?**  
A: "MLflow tracks model metrics over time. Set up alerts for accuracy drops, then trigger automated retraining."

### Next Steps

1. **Proof of Concept**: Deploy with sample of real transaction data (1 month)
2. **Validation**: Compare approval rates before/after Smart Checkout
3. **Production Rollout**: Phased deployment by geography or merchant segment
4. **Continuous Optimization**: Monitor, iterate, and improve

**Call to Action**:  
"Let's schedule a follow-up to discuss your specific use case and deployment timeline."

---

## Closing

**"We've shown you how to turn every payment authorization into an opportunity—using AI, real-time analytics, and the power of the Databricks Lakehouse. The result: more revenue, less risk, and happier customers."**

**"Questions?"**

---

## Post-Demo Follow-Up

- [ ] Send demo recording link
- [ ] Share Databricks workspace access (read-only)
- [ ] Provide README and deployment guide
- [ ] Schedule technical deep-dive session
- [ ] Discuss customization requirements
- [ ] Define POC scope and timeline

---

**Demo completed by**: _________________  
**Date**: _________________  
**Audience feedback**: _________________
