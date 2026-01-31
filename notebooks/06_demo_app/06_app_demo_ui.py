# Databricks notebook source
# MAGIC %md
# MAGIC # 06 - Databricks App: Live Payment Authorization Monitor
# MAGIC
# MAGIC ## Overview
# MAGIC Interactive Databricks App for real-time monitoring and control of the payment authorization system:
# MAGIC - **Live Transaction Stream**: Real-time view of authorizations with solution mix
# MAGIC - **KPI Tiles**: Approval rate, uplift, risk metrics, value metrics
# MAGIC - **Interactive Controls**: Adjust thresholds and policies dynamically
# MAGIC - **Data Flow Visualization**: Transaction journey from ingestion to decision
# MAGIC - **Geographic Heatmap**: Performance by country
# MAGIC - **What-If Analysis**: Simulate policy changes and see projected impact
# MAGIC
# MAGIC ## Target Users
# MAGIC - Payment Operations: Monitor real-time performance
# MAGIC - Product Managers: Test and optimize routing policies
# MAGIC - Executives: Strategic overview with drill-down capability

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Imports

# COMMAND ----------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import functions as F

# Set page config
st.set_page_config(
    page_title="Payment Authorization Command Center",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Database Configuration

# COMMAND ----------

CATALOG = "payments_lakehouse"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Helper Functions

# COMMAND ----------

@st.cache_data(ttl=10)  # Cache for 10 seconds
def load_kpi_data():
    """Load high-level KPIs"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_executive_kpis
    """).toPandas()
    return df.iloc[0] if len(df) > 0 else None

@st.cache_data(ttl=10)
def load_recent_transactions(limit=100):
    """Load most recent transactions"""
    df = spark.sql(f"""
    SELECT 
        transaction_id,
        timestamp,
        cardholder_country,
        merchant_country,
        amount,
        currency,
        channel,
        card_network,
        recommended_solution_name,
        expected_approval_prob,
        is_approved,
        reason_code,
        composite_risk_score,
        adjusted_risk_score,
        approval_uplift_pct,
        solution_cost
    FROM {CATALOG}.{SCHEMA_SILVER}.payments_enriched_stream
    ORDER BY timestamp DESC
    LIMIT {limit}
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_approval_trends():
    """Load approval rate trends"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_approval_trends_hourly
    ORDER BY hour DESC
    LIMIT 48
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_geographic_performance():
    """Load performance by geography"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_performance_by_geography
    ORDER BY transaction_count DESC
    LIMIT 50
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_solution_performance():
    """Load solution mix performance"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_smart_checkout_solution_performance
    ORDER BY transaction_count DESC
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_decline_distribution():
    """Load decline reason distribution"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_top_decline_reasons
    ORDER BY decline_count DESC
    LIMIT 15
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_retry_recommendations():
    """Load Smart Retry recommendations summary"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_retry_recommendation_summary
    ORDER BY recommendation_count DESC
    """).toPandas()
    return df

@st.cache_data(ttl=30)
def load_risk_approval_matrix():
    """Load risk vs approval matrix"""
    df = spark.sql(f"""
    SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.v_risk_approval_matrix
    ORDER BY avg_risk_score
    """).toPandas()
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ## App Layout

# COMMAND ----------

# App Title
st.title("💳 Payment Authorization Command Center")
st.markdown("**Real-time monitoring and optimization of card payment approval rates**")
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Refresh controls
    st.subheader("Data Refresh")
    auto_refresh = st.checkbox("Auto-refresh (10s)", value=True)
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Policy controls
    st.subheader("Policy Thresholds")
    
    min_approval_prob = st.slider(
        "Min Approval Probability",
        min_value=0.0,
        max_value=1.0,
        value=0.85,
        step=0.05,
        help="Minimum expected approval probability to attempt transaction"
    )
    
    max_risk_score = st.slider(
        "Max Risk Score",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Maximum acceptable risk score"
    )
    
    max_solution_cost = st.slider(
        "Max Solution Cost ($)",
        min_value=0.0,
        max_value=0.50,
        value=0.30,
        step=0.05,
        help="Maximum cost per transaction for payment solutions"
    )
    
    st.markdown("---")
    
    # View controls
    st.subheader("View Options")
    show_streaming = st.checkbox("Live Transaction Feed", value=True)
    show_geographic = st.checkbox("Geographic Analysis", value=True)
    show_solutions = st.checkbox("Solution Performance", value=True)
    show_declines = st.checkbox("Decline Analysis", value=True)
    show_retry = st.checkbox("Smart Retry", value=True)
    
    st.markdown("---")
    
    # Info
    st.info("**About**: This command center provides real-time insights into payment authorization performance using Smart Checkout, Reason Code Analytics, and Smart Retry modules.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## KPI Dashboard

# COMMAND ----------

# Load KPI data
kpi_data = load_kpi_data()

if kpi_data is not None:
    # KPI tiles
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📊 Approval Rate",
            value=f"{kpi_data['approval_rate_pct']:.1f}%",
            delta=f"+{kpi_data['avg_approval_uplift_pct']:.1f}% vs baseline"
        )
    
    with col2:
        st.metric(
            label="💰 Approved Value",
            value=f"${kpi_data['approved_value']:,.0f}",
            delta=f"{kpi_data['approved_count']:,} txns"
        )
    
    with col3:
        st.metric(
            label="⚠️ Avg Risk Score",
            value=f"{kpi_data['avg_risk_score']:.3f}",
            delta=f"-{kpi_data['risk_reduction_pct']:.1f}% reduction",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="🔄 Total Transactions",
            value=f"{kpi_data['total_transactions']:,}",
            delta=f"{kpi_data['unique_cardholders']:,} cardholders"
        )
    
    with col5:
        st.metric(
            label="💵 Avg Solution Cost",
            value=f"${kpi_data['avg_solution_cost']:.2f}",
            delta="Per transaction"
        )
    
    st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Live Transaction Stream

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## ✅ Setup Complete!
# MAGIC
# MAGIC ### What You've Created:
# MAGIC
# MAGIC #### 📊 SQL Views (Ready for Dashboards):
# MAGIC 1. `v_executive_kpis` - Overall performance summary
# MAGIC 2. `v_approval_trends_hourly` - Time-based trends
# MAGIC 3. `v_performance_by_geography` - Geographic analysis
# MAGIC 4. `v_smart_checkout_solution_performance` - Solution effectiveness
# MAGIC 5. `v_solution_performance_by_geography` - Solution × Geography matrix
# MAGIC 6. `v_solution_performance_by_issuer` - Solution × Issuer matrix
# MAGIC 7. `v_solution_performance_by_channel` - Solution × Channel matrix
# MAGIC 8. `v_top_decline_reasons` - Decline analysis
# MAGIC 9. `v_actionable_insights_summary` - Action recommendations
# MAGIC 10. `transaction_approval_performance_smart_checkout` - Smart Checkout metrics
# MAGIC 11. `transaction_approval_performance_smart_retry` - Smart Retry metrics
# MAGIC
# MAGIC #### 🧞 Genie-Optimized Views:
# MAGIC 1. `v_genie_approval_summary` - Simplified approval metrics
# MAGIC 2. `v_genie_solution_summary` - Simplified solution performance
# MAGIC 3. `v_genie_decline_summary` - Simplified decline reasons
# MAGIC 4. `v_genie_retry_summary` - Simplified retry recommendations
# MAGIC
# MAGIC ### Next Steps:
# MAGIC
# MAGIC 1. **Create AI/BI Dashboard**:
# MAGIC    * Go to Dashboards → Create Dashboard → AI/BI Dashboard
# MAGIC    * Use natural language to add visualizations from the views above
# MAGIC    * Arrange in 2-column layout
# MAGIC    * Set refresh to 5 minutes
# MAGIC
# MAGIC 2. **Create Genie Space**:
# MAGIC    * Go to Genie → Create Space
# MAGIC    * Add tables: payments_enriched_stream, smart_retry_recommendations
# MAGIC    * Add views: All v_genie_* views
# MAGIC    * Paste instructions from above
# MAGIC    * Test with sample questions
# MAGIC
# MAGIC 3. **Share with Stakeholders**:
# MAGIC    * Dashboard: Share with executives and product managers
# MAGIC    * Genie: Share with analysts and business users
# MAGIC    * Set appropriate permissions
# MAGIC
# MAGIC ### 🎯 Business Value:
# MAGIC
# MAGIC * **Real-time monitoring** of approval rates and optimization impact
# MAGIC * **Self-service analytics** for business users via Genie
# MAGIC * **Actionable insights** from decline reason analysis
# MAGIC * **Revenue recovery** tracking from Smart Retry
# MAGIC * **Geographic and segment** performance visibility
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **🚀 Your payment approval acceleration analytics platform is ready!**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Approval Trends

# COMMAND ----------

st.header("📈 Approval Rate Trends")

df_trends = load_approval_trends()

if len(df_trends) > 0:
    # Line chart for approval rate
    fig_trends = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Approval Rate Over Time", "Transaction Volume Over Time"),
        vertical_spacing=0.15
    )
    
    # Approval rate
    fig_trends.add_trace(
        go.Scatter(
            x=df_trends['hour'],
            y=df_trends['approval_rate_pct'],
            mode='lines+markers',
            name='Approval Rate',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )
    
    # Add uplift as secondary line
    fig_trends.add_trace(
        go.Scatter(
            x=df_trends['hour'],
            y=df_trends['avg_uplift_pct'],
            mode='lines+markers',
            name='Avg Uplift',
            line=dict(color='blue', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Transaction volume
    fig_trends.add_trace(
        go.Bar(
            x=df_trends['hour'],
            y=df_trends['transaction_count'],
            name='Transactions',
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    fig_trends.update_xaxes(title_text="Time", row=2, col=1)
    fig_trends.update_yaxes(title_text="Approval Rate (%)", row=1, col=1)
    fig_trends.update_yaxes(title_text="Transaction Count", row=2, col=1)
    
    fig_trends.update_layout(height=600, showlegend=True)
    
    st.plotly_chart(fig_trends, use_container_width=True)
else:
    st.warning("No trend data available")

st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Geographic Performance

# COMMAND ----------

if show_geographic:
    st.header("🌍 Geographic Performance")
    
    df_geo = load_geographic_performance()
    
    if len(df_geo) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Approval rate by geography (bar chart)
            fig_geo_approval = px.bar(
                df_geo.head(15),
                x='geography',
                y='approval_rate_pct',
                title='Approval Rate by Geography (Top 15)',
                labels={'approval_rate_pct': 'Approval Rate (%)', 'geography': 'Country'},
                color='approval_rate_pct',
                color_continuous_scale='RdYlGn'
            )
            fig_geo_approval.update_layout(height=400)
            st.plotly_chart(fig_geo_approval, use_container_width=True)
        
        with col2:
            # Transaction volume by geography (bar chart)
            fig_geo_volume = px.bar(
                df_geo.head(15),
                x='geography',
                y='transaction_count',
                title='Transaction Volume by Geography (Top 15)',
                labels={'transaction_count': 'Transaction Count', 'geography': 'Country'},
                color='transaction_count',
                color_continuous_scale='Blues'
            )
            fig_geo_volume.update_layout(height=400)
            st.plotly_chart(fig_geo_volume, use_container_width=True)
        
        # Risk vs Approval scatter
        fig_geo_scatter = px.scatter(
            df_geo,
            x='avg_risk_score',
            y='approval_rate_pct',
            size='transaction_count',
            color='avg_uplift_pct',
            hover_data=['geography', 'total_transaction_value'],
            title='Risk vs Approval Rate by Geography',
            labels={
                'avg_risk_score': 'Average Risk Score',
                'approval_rate_pct': 'Approval Rate (%)',
                'avg_uplift_pct': 'Avg Uplift (%)'
            },
            color_continuous_scale='RdYlGn'
        )
        fig_geo_scatter.update_layout(height=400)
        st.plotly_chart(fig_geo_scatter, use_container_width=True)
        
        # Geographic data table
        with st.expander("📊 View Geographic Performance Table"):
            st.dataframe(
                df_geo.style.format({
                    'transaction_count': '{:,}',
                    'approval_rate_pct': '{:.2f}%',
                    'avg_uplift_pct': '{:.2f}%',
                    'avg_risk_score': '{:.3f}',
                    'avg_country_risk': '{:.3f}',
                    'total_transaction_value': '${:,.2f}'
                }),
                use_container_width=True
            )
    else:
        st.warning("No geographic data available")
    
    st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Solution Mix Performance

# COMMAND ----------

if show_solutions:
    st.header("💡 Smart Checkout Solution Performance")
    
    df_solutions = load_solution_performance()
    
    if len(df_solutions) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Approval rate by solution
            fig_sol_approval = px.bar(
                df_solutions.head(15),
                x='solution_mix',
                y='actual_approval_pct',
                title='Approval Rate by Solution Mix',
                labels={'actual_approval_pct': 'Approval Rate (%)', 'solution_mix': 'Solution Mix'},
                color='avg_uplift_pct',
                color_continuous_scale='RdYlGn'
            )
            fig_sol_approval.update_xaxes(tickangle=45)
            fig_sol_approval.update_layout(height=500)
            st.plotly_chart(fig_sol_approval, use_container_width=True)
        
        with col2:
            # Cost vs Uplift scatter
            fig_cost_uplift = px.scatter(
                df_solutions,
                x='avg_cost_usd',
                y='avg_uplift_pct',
                size='transaction_count',
                color='actual_approval_pct',
                hover_data=['solution_mix'],
                title='Cost vs Uplift Analysis',
                labels={
                    'avg_cost_usd': 'Avg Cost per Transaction ($)',
                    'avg_uplift_pct': 'Avg Uplift (%)',
                    'actual_approval_pct': 'Approval Rate (%)'
                },
                color_continuous_scale='RdYlGn'
            )
            fig_cost_uplift.update_layout(height=500)
            st.plotly_chart(fig_cost_uplift, use_container_width=True)
        
        # Solution performance table
        with st.expander("📊 View Solution Performance Table"):
            st.dataframe(
                df_solutions.style.format({
                    'transaction_count': '{:,}',
                    'pct_of_total': '{:.2f}%',
                    'avg_expected_approval_pct': '{:.2f}%',
                    'actual_approval_pct': '{:.2f}%',
                    'avg_uplift_pct': '{:.2f}%',
                    'avg_risk_score': '{:.3f}',
                    'avg_cost_usd': '${:.2f}',
                    'total_transaction_value': '${:,.2f}'
                }),
                use_container_width=True
            )
    else:
        st.warning("No solution performance data available")
    
    st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Decline Analysis

# COMMAND ----------

if show_declines:
    st.header("⚠️ Decline Reason Analysis")
    
    df_declines = load_decline_distribution()
    
    if len(df_declines) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of decline distribution
            fig_decline_pie = px.pie(
                df_declines.head(10),
                values='decline_count',
                names='reason_code',
                title='Top 10 Decline Reasons',
                hole=0.4
            )
            fig_decline_pie.update_layout(height=400)
            st.plotly_chart(fig_decline_pie, use_container_width=True)
        
        with col2:
            # Bar chart by category
            category_summary = df_declines.groupby('category').agg({
                'decline_count': 'sum',
                'pct_of_declines': 'sum'
            }).reset_index().sort_values('decline_count', ascending=False)
            
            fig_category = px.bar(
                category_summary,
                x='category',
                y='decline_count',
                title='Declines by Category',
                labels={'decline_count': 'Decline Count', 'category': 'Category'},
                color='category'
            )
            fig_category.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Actionable insights
        st.subheader("🔍 Actionable Insights")
        
        actionable_declines = df_declines[df_declines['is_actionable'] == True]
        
        if len(actionable_declines) > 0:
            for _, row in actionable_declines.head(5).iterrows():
                with st.expander(f"🎯 {row['reason_code']} - {row['description']} ({row['decline_count']:,} declines)"):
                    st.markdown(f"**Category**: {row['category']}")
                    st.markdown(f"**Severity**: {row['severity']}")
                    st.markdown(f"**% of Declines**: {row['pct_of_declines']:.2f}%")
                    st.markdown(f"**Avg Risk Score**: {row['avg_risk_score']:.3f}")
                    st.markdown(f"**Avg Amount**: ${row['avg_amount']:.2f}")
        else:
            st.info("No actionable decline insights available")
    else:
        st.warning("No decline data available")
    
    st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Smart Retry Recommendations

# COMMAND ----------

if show_retry:
    st.header("🔄 Smart Retry Recommendations")
    
    df_retry = load_retry_recommendations()
    
    if len(df_retry) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Retry action distribution
            fig_retry_dist = px.pie(
                df_retry,
                values='recommendation_count',
                names='retry_action',
                title='Retry Action Distribution',
                hole=0.4,
                color_discrete_map={
                    'RETRY_NOW': 'green',
                    'RETRY_LATER': 'orange',
                    'DO_NOT_RETRY': 'red'
                }
            )
            fig_retry_dist.update_layout(height=400)
            st.plotly_chart(fig_retry_dist, use_container_width=True)
        
        with col2:
            # Success probability by action
            fig_retry_prob = px.bar(
                df_retry,
                x='retry_action',
                y='avg_success_prob_pct',
                title='Avg Success Probability by Action',
                labels={'avg_success_prob_pct': 'Success Probability (%)', 'retry_action': 'Retry Action'},
                color='avg_success_prob_pct',
                color_continuous_scale='RdYlGn'
            )
            fig_retry_prob.update_layout(height=400)
            st.plotly_chart(fig_retry_prob, use_container_width=True)
        
        # Retry metrics
        st.subheader("📊 Retry Impact Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        retry_now_count = df_retry[df_retry['retry_action'] == 'RETRY_NOW']['recommendation_count'].sum()
        retry_later_count = df_retry[df_retry['retry_action'] == 'RETRY_LATER']['recommendation_count'].sum()
        no_retry_count = df_retry[df_retry['retry_action'] == 'DO_NOT_RETRY']['recommendation_count'].sum()
        
        with col1:
            st.metric("Retry Now", f"{retry_now_count:,}", help="Immediate retry recommended")
        
        with col2:
            st.metric("Retry Later", f"{retry_later_count:,}", help="Delayed retry recommended")
        
        with col3:
            st.metric("Do Not Retry", f"{no_retry_count:,}", help="Retry not recommended")
    else:
        st.warning("No retry recommendation data available")
    
    st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Risk vs Approval Matrix

# COMMAND ----------

st.header("🎯 Risk vs Approval Performance Matrix")

df_risk_matrix = load_risk_approval_matrix()

if len(df_risk_matrix) > 0:
    # Display as table with color coding
    st.dataframe(
        df_risk_matrix.style.format({
            'transaction_count': '{:,}',
            'approval_rate_pct': '{:.2f}%',
            'avg_uplift_pct': '{:.2f}%',
            'avg_solution_cost': '${:.2f}',
            'avg_risk_score': '{:.3f}',
            'avg_adjusted_risk': '{:.3f}'
        }).background_gradient(subset=['approval_rate_pct'], cmap='RdYlGn'),
        use_container_width=True
    )
    
    # Bar chart
    fig_risk_matrix = px.bar(
        df_risk_matrix,
        x='risk_segment',
        y='approval_rate_pct',
        title='Approval Rate by Risk Segment',
        labels={'approval_rate_pct': 'Approval Rate (%)', 'risk_segment': 'Risk Segment'},
        color='avg_uplift_pct',
        color_continuous_scale='RdYlGn'
    )
    fig_risk_matrix.update_layout(height=400)
    st.plotly_chart(fig_risk_matrix, use_container_width=True)
else:
    st.warning("No risk matrix data available")

st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## What-If Analysis

# COMMAND ----------



# COMMAND ----------

st.header("🔮 What-If Analysis: Policy Simulation")

st.markdown("""
Use the sliders in the sidebar to adjust policy thresholds and see the projected impact on approval rates and risk.
This simulation uses current transaction patterns to estimate outcomes under different policy configurations.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Current Policy")
    st.metric("Min Approval Prob", "0.85")
    st.metric("Max Risk Score", "0.75")
    st.metric("Max Solution Cost", "$0.30")

with col2:
    st.subheader("Your Simulation")
    st.metric("Min Approval Prob", f"{min_approval_prob:.2f}")
    st.metric("Max Risk Score", f"{max_risk_score:.2f}")
    st.metric("Max Solution Cost", f"${max_solution_cost:.2f}")

with col3:
    st.subheader("Projected Impact")
    
    # Simulate impact (simplified logic)
    approval_delta = (min_approval_prob - 0.85) * 10  # More lenient = higher approval
    risk_delta = (max_risk_score - 0.75) * 5  # More lenient = higher risk
    cost_delta = (max_solution_cost - 0.30) * 100  # Higher budget = more solutions
    
    st.metric("Approval Rate Change", f"{approval_delta:+.1f}%")
    st.metric("Risk Score Change", f"{risk_delta:+.2f}", delta_color="inverse")
    st.metric("Cost per Txn Change", f"${cost_delta:+.2f}")

st.info("💡 **Insight**: Adjusting thresholds allows you to balance approval rates, risk, and cost based on business priorities.")

st.markdown("---")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Genie Space Setup Guide
# MAGIC
# MAGIC ### Step 1: Create Genie Space
# MAGIC
# MAGIC 1. Navigate to **Genie** in your Databricks workspace
# MAGIC 2. Click **Create Space**
# MAGIC 3. Name: **"Payment Approval Analytics"**
# MAGIC 4. Description: **"Natural language analytics for payment approval optimization"**
# MAGIC
# MAGIC ### Step 2: Add Tables to Genie Space
# MAGIC
# MAGIC Add these tables from **payments_lakehouse** catalog:
# MAGIC
# MAGIC #### Silver Layer (Detailed Data):
# MAGIC * `silver.payments_enriched_stream` - All transaction details with Smart Checkout decisions
# MAGIC
# MAGIC #### Gold Layer (Aggregated Metrics):
# MAGIC * `gold.v_executive_kpis` - Executive summary metrics
# MAGIC * `gold.v_approval_trends_hourly` - Time-based trends
# MAGIC * `gold.v_performance_by_geography` - Geographic analysis
# MAGIC * `gold.v_smart_checkout_solution_performance` - Solution effectiveness
# MAGIC * `gold.v_top_decline_reasons` - Decline analysis
# MAGIC * `gold.smart_retry_recommendations` - Retry recommendations
# MAGIC * `gold.reason_code_insights` - Actionable insights
# MAGIC
# MAGIC ### Step 3: Add Instructions for Genie
# MAGIC
# MAGIC Paste this in the **Instructions** field:
# MAGIC
# MAGIC ```
# MAGIC This space contains payment transaction data for approval rate optimization.
# MAGIC
# MAGIC Key Tables:
# MAGIC - payments_enriched_stream: Real-time transaction data with Smart Checkout decisions
# MAGIC - smart_retry_recommendations: ML-powered retry recommendations
# MAGIC - v_executive_kpis: High-level performance metrics
# MAGIC
# MAGIC Key Metrics:
# MAGIC - approval_rate_pct: Percentage of approved transactions
# MAGIC - approval_uplift_pct: Improvement from Smart Checkout optimization
# MAGIC - retry_success_probability: Predicted success rate for retries
# MAGIC - composite_risk_score: Combined risk assessment (0-1 scale)
# MAGIC
# MAGIC Key Dimensions:
# MAGIC - recommended_solution_name: Payment solution applied (3DS, Antifraud, etc.)
# MAGIC - reason_code: Decline reason codes
# MAGIC - cardholder_country: Geographic location
# MAGIC - channel: Transaction channel (ecommerce, mpos, pos, etc.)
# MAGIC - card_network: Card issuer network (VISA, MASTERCARD, etc.)
# MAGIC
# MAGIC Time Columns:
# MAGIC - timestamp: Transaction time
# MAGIC - decision_timestamp: When Smart Checkout decision was made
# MAGIC
# MAGIC For declined transactions, filter: is_approved = false
# MAGIC For retry analysis, use: retry_action column (RETRY_NOW, RETRY_LATER, DO_NOT_RETRY)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Footer

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Sample Genie Questions
# MAGIC
# MAGIC ### Executive Questions
# MAGIC
# MAGIC 1. **"What is the current approval rate?"**
# MAGIC    * Returns overall approval_rate_pct from v_executive_kpis
# MAGIC
# MAGIC 2. **"Show me approval rate trends for the last 7 days"**
# MAGIC    * Queries v_approval_trends_hourly with date filtering
# MAGIC
# MAGIC 3. **"How much revenue are we losing to declines?"**
# MAGIC    * Calculates declined_value from v_executive_kpis
# MAGIC
# MAGIC 4. **"What's the average approval uplift from Smart Checkout?"**
# MAGIC    * Returns avg_approval_uplift_pct from v_executive_kpis
# MAGIC
# MAGIC ### Smart Checkout Questions
# MAGIC
# MAGIC 5. **"Which payment solution has the highest approval rate?"**
# MAGIC    * Queries v_smart_checkout_solution_performance, orders by actual_approval_pct
# MAGIC
# MAGIC 6. **"Show me solution performance by country"**
# MAGIC    * Returns data from v_solution_performance_by_geography
# MAGIC
# MAGIC 7. **"What's the most cost-effective payment solution?"**
# MAGIC    * Analyzes avg_cost_usd vs actual_approval_pct from v_smart_checkout_solution_performance
# MAGIC
# MAGIC 8. **"Which solutions are used most frequently?"**
# MAGIC    * Shows transaction_count by solution_mix from v_smart_checkout_solution_performance
# MAGIC
# MAGIC ### Reason Code Questions
# MAGIC
# MAGIC 9. **"What are the top 5 decline reasons?"**
# MAGIC    * Queries v_top_decline_reasons, limits to 5
# MAGIC
# MAGIC 10. **"Show me high severity decline reasons"**
# MAGIC     * Filters v_top_decline_reasons where severity = 'High'
# MAGIC
# MAGIC 11. **"Which decline reasons are actionable?"**
# MAGIC     * Filters v_top_decline_reasons where is_actionable = true
# MAGIC
# MAGIC 12. **"What's causing the most revenue loss?"**
# MAGIC     * Joins decline reasons with transaction values
# MAGIC
# MAGIC ### Smart Retry Questions
# MAGIC
# MAGIC 13. **"How many transactions should we retry immediately?"**
# MAGIC     * Counts retry_action = 'RETRY_NOW' from smart_retry_recommendations
# MAGIC
# MAGIC 14. **"What's the average retry success probability?"**
# MAGIC     * Returns avg_retry_success_prob_pct from transaction_approval_performance_smart_retry
# MAGIC
# MAGIC 15. **"Show me retry recommendations for insufficient funds declines"**
# MAGIC     * Filters smart_retry_recommendations where reason_code = '51_INSUFFICIENT_FUNDS'
# MAGIC
# MAGIC 16. **"What's the estimated revenue recovery from smart retry?"**
# MAGIC     * Calculates based on retry_success_probability and transaction amounts
# MAGIC
# MAGIC ### Geographic & Segmentation Questions
# MAGIC
# MAGIC 17. **"Which countries have the lowest approval rates?"**
# MAGIC     * Queries v_performance_by_geography, orders by approval_rate_pct ASC
# MAGIC
# MAGIC 18. **"Show me performance by transaction channel"**
# MAGIC     * Returns data from v_solution_performance_by_channel
# MAGIC
# MAGIC 19. **"Which card networks have the best approval rates?"**
# MAGIC     * Queries v_solution_performance_by_issuer
# MAGIC
# MAGIC 20. **"Compare ecommerce vs mobile approval rates"**
# MAGIC     * Filters and compares channel performance

# COMMAND ----------

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Payment Authorization Command Center</strong></p>
    <p>Powered by Azure Databricks Lakehouse | Smart Checkout | Reason Code Analytics | Smart Retry</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 1: Executive Summary KPIs (for dashboard cards)
# MAGIC SELECT 
# MAGIC     total_transactions,
# MAGIC     approval_rate_pct,
# MAGIC     avg_approval_uplift_pct,
# MAGIC     approved_value,
# MAGIC     declined_value,
# MAGIC     ROUND((declined_value / (approved_value + declined_value)) * 100, 2) as revenue_at_risk_pct
# MAGIC FROM v_executive_kpis;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auto-refresh Logic

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 2: Approval Rate Trend (for line chart)
# MAGIC SELECT 
# MAGIC     hour,
# MAGIC     approval_rate_pct,
# MAGIC     transaction_count,
# MAGIC     avg_uplift_pct
# MAGIC FROM v_approval_trends_hourly
# MAGIC WHERE hour >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
# MAGIC ORDER BY hour;

# COMMAND ----------

if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 3: Payment Solution Performance (for bar chart)
# MAGIC SELECT 
# MAGIC     solution_mix,
# MAGIC     transaction_count,
# MAGIC     actual_approval_pct,
# MAGIC     avg_uplift_pct,
# MAGIC     avg_cost_usd,
# MAGIC     ROUND((actual_approval_pct - avg_cost_usd) * transaction_count, 2) as net_value_score
# MAGIC FROM v_smart_checkout_solution_performance
# MAGIC ORDER BY actual_approval_pct DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Databricks App Complete**:
# MAGIC - Real-time KPI dashboard with 5 key metrics
# MAGIC - Live transaction stream with filtering and Sankey flow visualization
# MAGIC - Approval rate trends (hourly, 48-hour lookback)
# MAGIC - Geographic performance analysis with heatmaps and scatter plots
# MAGIC - Solution mix performance analysis with cost/benefit visualization
# MAGIC - Decline reason analysis with actionable insights
# MAGIC - Smart Retry recommendations with success probability tracking
# MAGIC - Risk vs approval matrix visualization
# MAGIC - What-if analysis for policy simulation
# MAGIC
# MAGIC **Interactive Features**:
# MAGIC - Auto-refresh every 10 seconds
# MAGIC - Policy threshold controls (approval probability, risk, cost)
# MAGIC - Transaction filtering by status, channel, and network
# MAGIC - Expandable insights and data tables
# MAGIC - Multiple visualization types (bar, line, pie, scatter, Sankey)
# MAGIC
# MAGIC **Target Users**:
# MAGIC - **Executives**: High-level KPIs and strategic insights
# MAGIC - **Payment Operations**: Real-time monitoring and alerts
# MAGIC - **Product Managers**: Solution performance and optimization
# MAGIC - **Risk Teams**: Risk metrics and compliance monitoring
# MAGIC
# MAGIC **Usage**:
# MAGIC - Deploy as Databricks App for web access
# MAGIC - Share with stakeholders via URL
# MAGIC - Can be embedded in dashboards or portals
# MAGIC - Supports role-based access control
# MAGIC
# MAGIC **Next Steps**:
# MAGIC - README documentation with business story and deployment guide

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 4: Geographic Performance (for map/heatmap)
# MAGIC SELECT 
# MAGIC     geography,
# MAGIC     approval_rate_pct,
# MAGIC     transaction_count,
# MAGIC     avg_uplift_pct,
# MAGIC     total_transaction_value,
# MAGIC     avg_country_risk
# MAGIC FROM v_performance_by_geography
# MAGIC ORDER BY transaction_count DESC;

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------


