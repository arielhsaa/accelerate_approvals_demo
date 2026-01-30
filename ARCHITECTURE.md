# Architecture Documentation

## System Architecture Overview

### High-Level Components

```
┌────────────────────────────────────────────────────────────────────────┐
│                     AZURE DATABRICKS LAKEHOUSE                          │
│                     (Unity Catalog Enabled)                             │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
        ┌───────────────────────────┴───────────────────────────┐
        │                                                         │
        ▼                                                         ▼
┌──────────────────┐                                    ┌──────────────────┐
│  DATA SOURCES    │                                    │  CONSUMPTION     │
├──────────────────┤                                    ├──────────────────┤
│ • Event Hubs     │                                    │ • Databricks SQL │
│ • Kafka          │                                    │ • Dashboards     │
│ • Payment APIs   │                                    │ • Genie          │
│ • External Risk  │                                    │ • Apps           │
│   (Moody's, etc) │                                    │ • API Endpoints  │
└──────────────────┘                                    └──────────────────┘
```

---

## Detailed Architecture

### 1. Data Ingestion Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (Raw)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ transactions_raw │  │ cardholders_dim  │               │
│  │ (streaming)      │  │ (batch)          │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌───────────────────────┐          │
│  │ merchants_dim    │  │ external_risk_signals │          │
│  │ (batch)          │  │ (batch + streaming)   │          │
│  └──────────────────┘  └───────────────────────┘          │
│                                                              │
│  ┌──────────────────┐                                      │
│  │ reason_code_dim  │                                      │
│  │ (reference)      │                                      │
│  └──────────────────┘                                      │
│                                                              │
│  Format: Delta Lake                                         │
│  Ingestion: Structured Streaming (real-time)                │
│  Latency: Sub-second to 10 seconds                          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Processing & Feature Engineering Layer

```
┌─────────────────────────────────────────────────────────────┐
│                   SILVER LAYER (Enriched)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      payments_enriched_stream                       │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  • Joins: cardholders + merchants + risk signals    │   │
│  │  • Features:                                         │   │
│  │    - Velocity (1h, 24h transaction counts)          │   │
│  │    - Behavioral (approval rates, patterns)          │   │
│  │    - Temporal (hour, day, is_salary_day)            │   │
│  │    - Composite risk score                           │   │
│  │  • Smart Checkout Decisions:                        │   │
│  │    - Recommended solution mix                       │   │
│  │    - Expected approval probability                  │   │
│  │    - Approval uplift percentage                     │   │
│  │    - Adjusted risk score                            │   │
│  │    - Cascading path (fallback options)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      retry_history                                   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  • Synthetic retry attempts with outcomes           │   │
│  │  • Features for ML model training                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Processing: Spark Structured Streaming                     │
│  Trigger: 5-10 second micro-batches                         │
│  Stateful: Window aggregations, joins                       │
└─────────────────────────────────────────────────────────────┘
```

### 3. Analytics & Insights Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     GOLD LAYER (Analytics)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  Smart Checkout Performance                     │        │
│  ├────────────────────────────────────────────────┤        │
│  │  • smart_checkout_performance                   │        │
│  │  • v_smart_checkout_solution_performance        │        │
│  │  • v_solution_performance_by_geography          │        │
│  │  • v_solution_performance_by_issuer             │        │
│  │  • v_solution_performance_by_channel            │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  Reason Code Analytics                          │        │
│  ├────────────────────────────────────────────────┤        │
│  │  • decline_distribution                         │        │
│  │  • decline_by_issuer                            │        │
│  │  • decline_by_geography                         │        │
│  │  • decline_by_merchant_cluster                  │        │
│  │  • decline_by_solution_mix                      │        │
│  │  • decline_by_channel                           │        │
│  │  • decline_trends (time series)                 │        │
│  │  • reason_code_insights (actionable)            │        │
│  │  • smart_checkout_config_recommendations        │        │
│  │  • decline_heatmap_issuer_reason                │        │
│  │  • v_top_decline_reasons                        │        │
│  │  • v_actionable_insights_summary                │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  Smart Retry Recommendations                    │        │
│  ├────────────────────────────────────────────────┤        │
│  │  • smart_retry_recommendations                  │        │
│  │  • retry_model_feature_importance               │        │
│  │  • v_retry_recommendation_summary               │        │
│  │  • v_retry_by_reason_code                       │        │
│  │  • v_retry_value_recovery                       │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  Executive & Cross-Functional                   │        │
│  ├────────────────────────────────────────────────┤        │
│  │  • v_executive_kpis                             │        │
│  │  • v_approval_trends_hourly                     │        │
│  │  • v_performance_by_geography                   │        │
│  │  • v_approval_funnel                            │        │
│  │  • v_risk_approval_matrix                       │        │
│  │  • v_merchant_segment_performance               │        │
│  │  • v_last_hour_performance                      │        │
│  │  • v_active_alerts                              │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  Aggregation: Batch (scheduled) or Streaming                │
│  Refresh: Every 5-60 minutes depending on view              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Smart Checkout Decision Engine

```
┌─────────────────────────────────────────────────────────────┐
│              SMART CHECKOUT DECISION FLOW                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Incoming Transaction           │
        │   (amount, channel, geo, risk)   │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Enumerate Solution Combos      │
        │   (50+ combinations)             │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Score Each Combination         │
        │   • Approval Uplift              │
        │   • Risk Reduction               │
        │   • Cost                         │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Apply Business Rules           │
        │   • Mandatory 3DS (EU)           │
        │   • High-risk MCC handling       │
        │   • Issuer preferences           │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Select Optimal Solution        │
        │   (max approval, min risk/cost)  │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Generate Cascading Path        │
        │   (fallback options if fail)     │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Return Decision                │
        │   • Solution name                │
        │   • Expected approval prob       │
        │   • Uplift %                     │
        │   • Adjusted risk                │
        │   • Cascading path               │
        └──────────────────────────────────┘
```

### Smart Retry ML Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 SMART RETRY ML PIPELINE                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴────────────────────┐
        ▼                                        ▼
┌──────────────────┐                  ┌──────────────────┐
│  Training Data   │                  │  Inference Data  │
│  (retry_history) │                  │  (new declines)  │
└──────────────────┘                  └──────────────────┘
        │                                        │
        ▼                                        │
┌──────────────────┐                            │
│  Feature Eng     │                            │
│  • Time features │                            │
│  • Risk scores   │                            │
│  • Issuer stats  │                            │
│  • Reason code   │                            │
└──────────────────┘                            │
        │                                        │
        ▼                                        │
┌──────────────────┐                            │
│  Train Model     │                            │
│  • GBT Classifier│                            │
│  • MLflow track  │                            │
│  • Model Registry│                            │
└──────────────────┘                            │
        │                                        │
        ▼                                        │
┌──────────────────┐                            │
│  Evaluate        │                            │
│  • AUC           │                            │
│  • Accuracy      │                            │
│  • Feature imp   │                            │
└──────────────────┘                            │
        │                                        │
        ▼                                        │
┌──────────────────┐                            │
│  Register Model  │◄───────────────────────────┘
│  (production)    │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Predict Retry   │
│  Success Prob    │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Classify Action │
│  • RETRY_NOW     │
│  • RETRY_LATER   │
│  • DO_NOT_RETRY  │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Calculate Delay │
│  (hours based on │
│   reason code)   │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Output          │
│  Recommendation  │
└──────────────────┘
```

---

## Technology Stack

### Databricks Components

- **Delta Lake**: Storage layer with ACID transactions, time travel, schema evolution
- **Spark Structured Streaming**: Real-time processing with micro-batching
- **Unity Catalog**: Data governance, lineage, access control
- **MLflow**: Model tracking, versioning, registry, deployment
- **Databricks SQL**: SQL analytics and dashboards
- **Genie**: Natural language query interface
- **Databricks Apps**: Interactive web applications (Streamlit-based)
- **Workflows**: Job orchestration and scheduling

### Languages & Libraries

- **Python 3.10+**: Primary language for notebooks
- **PySpark**: Distributed data processing
- **Spark SQL**: SQL queries and transformations
- **Pandas**: Data manipulation (for small datasets in App)
- **Plotly**: Interactive visualizations
- **MLlib**: Machine learning (Gradient Boosted Trees)

### Azure Services (Production)

- **Azure Databricks**: Core platform
- **Azure Data Lake Storage Gen2**: Delta Lake storage
- **Azure Event Hubs**: Streaming ingestion
- **Azure Key Vault**: Secrets management
- **Azure Monitor**: Observability and alerting
- **Azure Active Directory**: Authentication and authorization

---

## Data Flow Sequence

### Transaction Lifecycle

```
1. INGESTION (Bronze)
   ├─ Transaction arrives via Event Hubs
   ├─ Written to transactions_raw (Delta)
   └─ Triggers: 10-second micro-batch

2. ENRICHMENT (Silver)
   ├─ Join with cardholders_dim
   ├─ Join with merchants_dim
   ├─ Join with external_risk_signals
   ├─ Calculate features (velocity, behavior, temporal)
   └─ Compute composite risk score

3. SMART CHECKOUT (Silver)
   ├─ Enumerate 50+ solution combinations
   ├─ Score each: approval uplift, risk reduction, cost
   ├─ Apply business rules (mandatory 3DS, issuer prefs)
   ├─ Select optimal solution
   └─ Write to payments_enriched_stream

4. ANALYTICS (Gold)
   ├─ Aggregate by dimensions (geo, issuer, merchant, etc.)
   ├─ Generate insights (reason code analysis)
   ├─ Calculate KPIs (approval rate, uplift, risk)
   └─ Write to Gold tables

5. ML INFERENCE (Gold - if declined)
   ├─ Extract features from declined transaction
   ├─ Load trained Smart Retry model
   ├─ Predict retry success probability
   ├─ Classify action (RETRY_NOW, RETRY_LATER, DO_NOT_RETRY)
   ├─ Calculate suggested delay
   └─ Write to smart_retry_recommendations

6. CONSUMPTION (Apps, Dashboards, APIs)
   ├─ Databricks App: Real-time monitoring
   ├─ SQL Dashboards: Executive KPIs
   ├─ Genie: Natural language queries
   └─ API Endpoints: Integration with payment gateway
```

---

## Performance Characteristics

### Latency

- **Streaming Ingestion**: Sub-second to 5 seconds
- **Smart Checkout Decision**: 100-500ms per transaction
- **ML Inference (Retry)**: 50-200ms per transaction
- **Dashboard Refresh**: 5-30 seconds (depending on query complexity)

### Throughput

- **Transactions/second**: 1,000-10,000 (with appropriate cluster sizing)
- **Daily volume**: 10M-100M transactions (scalable with auto-scaling)

### Storage

- **Bronze**: ~1-5 TB/month (depending on transaction volume)
- **Silver**: ~2-10 TB/month (with features)
- **Gold**: ~500 GB - 2 TB/month (aggregated)
- **Retention**: 90 days hot, 1 year warm, 7 years cold (configurable)

---

## Scalability & High Availability

### Horizontal Scaling

- **Auto-scaling clusters**: Scale from 2 to 50+ workers based on load
- **Partitioning**: Transactions partitioned by date and geography
- **Parallel processing**: Spark distributes work across cluster

### Fault Tolerance

- **Checkpointing**: Structured Streaming checkpoints for exactly-once semantics
- **Delta Lake transactions**: ACID guarantees prevent data corruption
- **Retry logic**: Failed jobs automatically retry with exponential backoff

### High Availability

- **Multi-region deployment**: Active-active across Azure regions
- **Data replication**: Delta Lake with geo-redundant storage
- **Monitoring & alerting**: Azure Monitor with PagerDuty integration

---

## Security & Compliance

### Data Security

- **Encryption at rest**: AES-256 encryption for all Delta tables
- **Encryption in transit**: TLS 1.2+ for all data movement
- **PII masking**: Dynamic data masking for sensitive fields
- **Secrets management**: Azure Key Vault integration

### Access Control

- **Unity Catalog RBAC**: Table, column, and row-level permissions
- **Azure AD integration**: SSO with MFA
- **Audit logging**: All access and changes logged to Azure Monitor

### Compliance

- **GDPR**: Right to be forgotten via Delta Lake time travel + DELETE
- **PCI-DSS**: Tokenization of card data, audit trails
- **SOC 2**: Databricks platform compliance

---

## Monitoring & Observability

### Metrics

- **Business Metrics**:
  - Approval rate, decline rate, uplift percentage
  - Transaction volume, value, counts
  - Model accuracy, prediction distribution

- **Technical Metrics**:
  - Streaming lag, processing time
  - Cluster utilization, auto-scaling events
  - Query performance, cache hit rates

### Alerting

- **Business Alerts**:
  - Approval rate drops below threshold
  - High decline volume for specific reason codes
  - Model prediction drift detected

- **Technical Alerts**:
  - Streaming job failures or lag > 1 minute
  - Cluster resource exhaustion
  - Data quality issues (null values, schema drift)

---

## Cost Optimization

### Compute

- **Auto-scaling**: Scale down during low traffic periods
- **Spot instances**: Use for non-critical workloads
- **Serverless SQL**: Pay-per-query for ad-hoc analytics

### Storage

- **Data lifecycle**: Move to cold storage after 90 days
- **Z-ordering**: Optimize table layout for frequent query patterns
- **Vacuum**: Remove old versions to reduce storage costs

### Optimization Techniques

- **Caching**: Cache frequently accessed tables in memory
- **Partitioning**: Prune partitions to reduce data scanned
- **Broadcast joins**: Use for small dimension tables

---

## Disaster Recovery

### Backup Strategy

- **Automated snapshots**: Delta Lake snapshots every hour
- **Geo-replication**: Replicate to secondary Azure region
- **Retention**: 7-day retention for Bronze, 30-day for Gold

### Recovery Procedures

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes
- **Failover**: Automated failover to secondary region

---

## Future Architecture Enhancements

1. **Real-Time Feature Store**: Centralized feature repository for consistent feature engineering
2. **Graph Database Integration**: Neo4j for fraud ring detection and network analysis
3. **Streaming ML**: Online learning with continuous model updates
4. **Multi-Cloud**: Hybrid deployment across AWS, Azure, GCP
5. **Edge Processing**: Lightweight decision engine deployed at payment gateway edge

---

**Last Updated**: 2026-01-30  
**Version**: 1.0  
**Owner**: Data & Analytics Team
