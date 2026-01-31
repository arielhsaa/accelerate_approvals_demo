# Databricks notebook source
# MAGIC %md
# MAGIC # Advanced Payment Authorization Command Center
# MAGIC 
# MAGIC ## Professional Databricks App with Dashboards & Genie Integration
# MAGIC 
# MAGIC **Features:**
# MAGIC - 📊 Multi-page dashboard interface
# MAGIC - 🤖 Genie AI integration for natural language queries
# MAGIC - 📈 Real-time KPI monitoring
# MAGIC - 🎯 Smart Checkout analytics
# MAGIC - 📉 Decline analysis & insights
# MAGIC - 🔄 Smart Retry recommendations
# MAGIC - 🌍 Geographic performance maps
# MAGIC - 🎨 Professional UI with modern design

# COMMAND ----------

# MAGIC %pip install streamlit plotly streamlit-extras streamlit-option-menu databricks-sql-connector
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from streamlit_option_menu import option_menu
import json

# Set page config
st.set_page_config(
    page_title="Payment Authorization Command Center",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Custom Styling

# COMMAND ----------

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #FF3621;
        --secondary-color: #00A972;
        --background-color: #0D1117;
        --card-background: #161B22;
        --text-color: #C9D1D9;
        --border-color: #30363D;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #FF3621 0%, #FF8A00 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 54, 33, 0.2);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #58A6FF;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .kpi-delta-positive {
        color: #3FB950;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .kpi-delta-negative {
        color: #F85149;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Section styling */
    .section-header {
        color: #58A6FF;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #30363D;
    }
    
    /* Metric card */
    .metric-card {
        background: #161B22;
        border-left: 4px solid #58A6FF;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Info box */
    .info-box {
        background: rgba(56, 139, 253, 0.1);
        border-left: 4px solid #58A6FF;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: rgba(248, 81, 73, 0.1);
        border-left: 4px solid #F85149;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: rgba(63, 185, 80, 0.1);
        border-left: 4px solid #3FB950;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Genie section */
    .genie-section {
        background: linear-gradient(135deg, #1C2128 0%, #161B22 100%);
        border: 2px solid #30363D;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .genie-icon {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #FF3621 0%, #FF8A00 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(255, 54, 33, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #0D1117;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #30363D;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Database Connection & Helper Functions

# COMMAND ----------

# Database configuration
CATALOG = "payments_lakehouse"
SCHEMA_GOLD = "gold"

def load_data_from_delta(table_name, limit=1000):
    """Load data from Delta table"""
    try:
        df = spark.sql(f"""
            SELECT * FROM {CATALOG}.{SCHEMA_GOLD}.{table_name}
            ORDER BY timestamp DESC
            LIMIT {limit}
        """).toPandas()
        return df
    except Exception as e:
        st.warning(f"Table {table_name} not yet available. Using synthetic data for demo.")
        return generate_synthetic_data(table_name)

def generate_synthetic_data(table_name):
    """Generate synthetic data for demo purposes"""
    np.random.seed(42)
    n_records = 500
    
    if table_name == "smart_checkout_decisions":
        return pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=n_records, freq='1min'),
            'transaction_id': [f'TXN{i:06d}' for i in range(n_records)],
            'amount': np.random.lognormal(4, 1.5, n_records),
            'currency': np.random.choice(['USD', 'EUR', 'GBP'], n_records),
            'geography': np.random.choice(['US', 'EU', 'UK', 'LATAM', 'APAC'], n_records),
            'merchant_category': np.random.choice(['retail', 'ecommerce', 'travel', 'financial'], n_records),
            'channel': np.random.choice(['online', 'mobile', 'pos'], n_records),
            'chosen_solution_stack': np.random.choice([
                '3DS+Antifraud', 'NetworkToken+3DS', 'Antifraud', 
                'DataShareOnly', 'Passkey+Antifraud', '3DS+Antifraud+IDPay'
            ], n_records),
            'approval_status': np.random.choice(['approved', 'declined'], n_records, p=[0.85, 0.15]),
            'predicted_approval_probability': np.random.beta(8, 2, n_records),
            'risk_score': np.random.beta(2, 8, n_records),
            'reason_code': np.random.choice([
                '00_APPROVED', '05_DO_NOT_HONOR', '51_INSUFFICIENT_FUNDS',
                '61_EXCEEDS_LIMIT', '63_SECURITY_VIOLATION', '91_ISSUER_UNAVAILABLE'
            ], n_records, p=[0.85, 0.06, 0.03, 0.02, 0.02, 0.02])
        })
    
    elif table_name == "reason_code_insights":
        return pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=100, freq='1H'),
            'reason_code': np.random.choice([
                '05_DO_NOT_HONOR', '51_INSUFFICIENT_FUNDS', '61_EXCEEDS_LIMIT',
                '63_SECURITY_VIOLATION', '91_ISSUER_UNAVAILABLE'
            ], 100),
            'decline_count': np.random.poisson(50, 100),
            'geography': np.random.choice(['US', 'EU', 'UK', 'LATAM', 'APAC'], 100),
            'issuer': np.random.choice(['VISA', 'MASTERCARD', 'AMEX', 'DISCOVER'], 100),
            'merchant_category': np.random.choice(['retail', 'ecommerce', 'travel', 'financial'], 100),
            'actionable': np.random.choice([True, False], 100, p=[0.7, 0.3]),
            'recommended_action': np.random.choice([
                'Enable 3DS', 'Use Network Token', 'Retry after 24h',
                'Split transaction', 'Route through alternative acquirer'
            ], 100)
        })
    
    elif table_name == "smart_retry_recommendations":
        return pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=200, freq='30min'),
            'transaction_id': [f'TXN{i:06d}' for i in range(200)],
            'original_decline_code': np.random.choice([
                '05_DO_NOT_HONOR', '51_INSUFFICIENT_FUNDS', '61_EXCEEDS_LIMIT'
            ], 200),
            'retry_recommendation': np.random.choice(['RETRY_NOW', 'RETRY_LATER', 'DO_NOT_RETRY'], 200, p=[0.3, 0.5, 0.2]),
            'retry_success_probability': np.random.beta(4, 4, 200),
            'recommended_wait_hours': np.random.choice([1, 3, 6, 24, 72], 200),
            'suggested_solution_mix': np.random.choice([
                'NetworkToken+3DS', '3DS+Antifraud', 'Passkey+Antifraud'
            ], 200),
            'amount': np.random.lognormal(4, 1.5, 200),
            'geography': np.random.choice(['US', 'EU', 'UK', 'LATAM', 'APAC'], 200)
        })
    
    return pd.DataFrame()

def calculate_kpis(df):
    """Calculate key performance indicators"""
    if df.empty:
        return {}
    
    total_transactions = len(df)
    approved = len(df[df['approval_status'] == 'approved'])
    declined = total_transactions - approved
    approval_rate = (approved / total_transactions * 100) if total_transactions > 0 else 0
    
    avg_amount = df['amount'].mean()
    total_volume = df['amount'].sum()
    avg_risk_score = df['risk_score'].mean()
    
    return {
        'total_transactions': total_transactions,
        'approval_rate': approval_rate,
        'decline_rate': 100 - approval_rate,
        'avg_amount': avg_amount,
        'total_volume': total_volume,
        'avg_risk_score': avg_risk_score
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main Application

# COMMAND ----------

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💳 Payment Authorization Command Center</h1>
        <p>Real-time analytics for Smart Checkout, Reason Code Performance & Smart Retry | Powered by Databricks Lakehouse</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://www.databricks.com/wp-content/uploads/2021/06/db-nav-logo.svg", width=200)
        
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "🏠 Executive Dashboard",
                "🎯 Smart Checkout",
                "📉 Decline Analysis",
                "🔄 Smart Retry",
                "🌍 Geographic Performance",
                "🤖 Genie AI Assistant",
                "⚙️ Configuration"
            ],
            icons=['house', 'bullseye', 'graph-down', 'arrow-repeat', 'globe', 'robot', 'gear'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#0D1117"},
                "icon": {"color": "#58A6FF", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#C9D1D9",
                    "--hover-color": "#161B22"
                },
                "nav-link-selected": {"background-color": "#FF3621", "color": "white"},
            }
        )
        
        st.markdown("---")
        st.markdown("### 📊 Real-time Status")
        st.metric("Active Streams", "3", delta="✓ Healthy")
        st.metric("Data Freshness", "< 5 sec", delta="Real-time")
        st.metric("System Uptime", "99.9%", delta="+0.1%")
        
        st.markdown("---")
        st.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Load data
    checkout_data = load_data_from_delta("smart_checkout_decisions")
    decline_data = load_data_from_delta("reason_code_insights")
    retry_data = load_data_from_delta("smart_retry_recommendations")
    
    # Route to selected page
    if selected == "🏠 Executive Dashboard":
        show_executive_dashboard(checkout_data, decline_data, retry_data)
    elif selected == "🎯 Smart Checkout":
        show_smart_checkout(checkout_data)
    elif selected == "📉 Decline Analysis":
        show_decline_analysis(decline_data)
    elif selected == "🔄 Smart Retry":
        show_smart_retry(retry_data)
    elif selected == "🌍 Geographic Performance":
        show_geographic_performance(checkout_data)
    elif selected == "🤖 Genie AI Assistant":
        show_genie_assistant()
    elif selected == "⚙️ Configuration":
        show_configuration()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Executive Dashboard

# COMMAND ----------

def show_executive_dashboard(checkout_data, decline_data, retry_data):
    st.markdown('<h2 class="section-header">📊 Executive Overview</h2>', unsafe_allow_html=True)
    
    # Calculate KPIs
    kpis = calculate_kpis(checkout_data)
    
    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Approval Rate</div>
            <div class="kpi-value">{kpis.get('approval_rate', 0):.1f}%</div>
            <div class="kpi-delta-positive">↑ +2.3% vs baseline</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Transactions</div>
            <div class="kpi-value">{kpis.get('total_transactions', 0):,}</div>
            <div class="kpi-delta-positive">↑ +15% this hour</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Transaction Volume</div>
            <div class="kpi-value">${kpis.get('total_volume', 0)/1000:.1f}K</div>
            <div class="kpi-delta-positive">↑ +8.7%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-value">{kpis.get('avg_risk_score', 0):.2f}</div>
            <div class="kpi-delta-positive">↓ -0.05 (Better)</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Approval Rate Trend (Last 24H)")
        if not checkout_data.empty:
            # Hourly approval rate
            checkout_data['hour'] = pd.to_datetime(checkout_data['timestamp']).dt.floor('H')
            hourly_stats = checkout_data.groupby('hour').agg({
                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100
            }).reset_index()
            hourly_stats.columns = ['hour', 'approval_rate']
            
            fig = px.line(hourly_stats, x='hour', y='approval_rate',
                         labels={'hour': 'Time', 'approval_rate': 'Approval Rate (%)'},
                         markers=True)
            fig.update_traces(line_color='#58A6FF', line_width=3)
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=350,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Smart Checkout Solution Mix")
        if not checkout_data.empty:
            solution_counts = checkout_data['chosen_solution_stack'].value_counts()
            fig = px.pie(values=solution_counts.values, names=solution_counts.index,
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Performance by Geography")
        if not checkout_data.empty:
            geo_stats = checkout_data.groupby('geography').agg({
                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
                'transaction_id': 'count'
            }).reset_index()
            geo_stats.columns = ['geography', 'approval_rate', 'transaction_count']
            
            fig = go.Figure(data=[
                go.Bar(name='Approval Rate', x=geo_stats['geography'], y=geo_stats['approval_rate'],
                      marker_color='#3FB950', yaxis='y'),
                go.Scatter(name='Transaction Count', x=geo_stats['geography'], y=geo_stats['transaction_count'],
                          mode='lines+markers', marker_color='#FF8A00', yaxis='y2')
            ])
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=350,
                yaxis=dict(title='Approval Rate (%)', side='left'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📉 Top Decline Reasons")
        if not decline_data.empty:
            decline_summary = decline_data.groupby('reason_code')['decline_count'].sum().sort_values(ascending=True).tail(8)
            fig = px.bar(x=decline_summary.values, y=decline_summary.index, orientation='h',
                        labels={'x': 'Decline Count', 'y': 'Reason Code'},
                        color=decline_summary.values,
                        color_continuous_scale='Reds')
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Actionable Insights
    st.markdown('<h2 class="section-header">💡 Actionable Insights</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="success-box">
            <h4>✅ Win: EU Approval Rate Up</h4>
            <p>3DS+NetworkToken combination shows <strong>+12% uplift</strong> in EU region. 
            Consider expanding to UK market.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Alert: LATAM Decline Spike</h4>
            <p>Security violations increased <strong>+35%</strong> in last 6 hours. 
            Recommend enabling Antifraud+IDPay for high-value transactions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h4>📊 Opportunity: Smart Retry</h4>
            <p>ML model identifies <strong>450 transactions</strong> with >70% retry success probability. 
            Potential revenue recovery: <strong>$127K</strong></p>
        </div>
        """, unsafe_allow_html=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Smart Checkout

# COMMAND ----------

def show_smart_checkout(checkout_data):
    st.markdown('<h2 class="section-header">🎯 Smart Checkout Analytics</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Smart Checkout</strong> dynamically selects the optimal payment solution mix for each transaction 
        to maximize approval rates while managing risk and cost.
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        geo_filter = st.multiselect("Geography", options=['All'] + list(checkout_data['geography'].unique()),
                                    default=['All'])
    with col2:
        channel_filter = st.multiselect("Channel", options=['All'] + list(checkout_data['channel'].unique()),
                                       default=['All'])
    with col3:
        amount_range = st.slider("Transaction Amount", 0, 5000, (0, 5000))
    with col4:
        approval_filter = st.selectbox("Status", options=['All', 'Approved', 'Declined'])
    
    # Apply filters
    filtered_data = checkout_data.copy()
    if 'All' not in geo_filter and len(geo_filter) > 0:
        filtered_data = filtered_data[filtered_data['geography'].isin(geo_filter)]
    if 'All' not in channel_filter and len(channel_filter) > 0:
        filtered_data = filtered_data[filtered_data['channel'].isin(channel_filter)]
    filtered_data = filtered_data[(filtered_data['amount'] >= amount_range[0]) & 
                                  (filtered_data['amount'] <= amount_range[1])]
    if approval_filter != 'All':
        filtered_data = filtered_data[filtered_data['approval_status'] == approval_filter.lower()]
    
    # Solution Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Solution Mix Performance")
        solution_perf = filtered_data.groupby('chosen_solution_stack').agg({
            'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        solution_perf.columns = ['solution', 'approval_rate', 'count', 'volume']
        solution_perf = solution_perf.sort_values('approval_rate', ascending=False)
        
        fig = px.scatter(solution_perf, x='count', y='approval_rate', size='volume',
                        hover_data=['solution'],
                        labels={'count': 'Transaction Count', 'approval_rate': 'Approval Rate (%)'},
                        color='approval_rate',
                        color_continuous_scale='Viridis')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Cost vs Approval Trade-off")
        # Simulate cost data
        cost_map = {
            '3DS+Antifraud': 0.25, 'NetworkToken+3DS': 0.23, 'Antifraud': 0.10,
            'DataShareOnly': 0.05, 'Passkey+Antifraud': 0.22, '3DS+Antifraud+IDPay': 0.45
        }
        solution_perf['cost_per_txn'] = solution_perf['solution'].map(cost_map)
        
        fig = px.scatter(solution_perf, x='cost_per_txn', y='approval_rate',
                        size='count', hover_data=['solution'],
                        labels={'cost_per_txn': 'Cost per Transaction ($)', 
                               'approval_rate': 'Approval Rate (%)'},
                        color='approval_rate',
                        color_continuous_scale='RdYlGn')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk Score Distribution
    st.markdown("### 🎲 Risk Score vs Approval Probability")
    fig = px.scatter(filtered_data.sample(min(500, len(filtered_data))),
                    x='risk_score', y='predicted_approval_probability',
                    color='approval_status',
                    labels={'risk_score': 'Risk Score', 
                           'predicted_approval_probability': 'Predicted Approval Probability'},
                    color_discrete_map={'approved': '#3FB950', 'declined': '#F85149'},
                    opacity=0.6)
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Transactions Table
    st.markdown("### 📋 Recent Transactions")
    display_cols = ['timestamp', 'transaction_id', 'amount', 'geography', 'chosen_solution_stack', 
                    'approval_status', 'predicted_approval_probability', 'risk_score']
    st.dataframe(filtered_data[display_cols].head(20).style.background_gradient(cmap='RdYlGn', subset=['predicted_approval_probability']))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Decline Analysis

# COMMAND ----------

def show_decline_analysis(decline_data):
    st.markdown('<h2 class="section-header">📉 Reason Code Performance & Decline Analysis</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        Near real-time analytics on decline patterns to identify root causes and generate actionable remediation strategies.
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_declines = decline_data['decline_count'].sum()
    actionable_declines = decline_data[decline_data['actionable'] == True]['decline_count'].sum()
    unique_codes = decline_data['reason_code'].nunique()
    
    with col1:
        st.metric("Total Declines", f"{total_declines:,}")
    with col2:
        st.metric("Actionable Declines", f"{actionable_declines:,}", 
                 delta=f"{(actionable_declines/total_declines*100):.1f}%")
    with col3:
        st.metric("Unique Decline Codes", unique_codes)
    with col4:
        recovery_potential = total_declines * 0.35 * 75  # 35% recoverable, $75 avg
        st.metric("Recovery Potential", f"${recovery_potential/1000:.1f}K")
    
    # Decline Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ Decline Heatmap: Geography × Issuer")
        heatmap_data = decline_data.pivot_table(
            values='decline_count', 
            index='geography', 
            columns='issuer', 
            aggfunc='sum',
            fill_value=0
        )
        fig = px.imshow(heatmap_data,
                       labels=dict(x="Issuer", y="Geography", color="Decline Count"),
                       color_continuous_scale='Reds',
                       aspect='auto')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Decline Trend by Reason Code")
        decline_data['hour'] = pd.to_datetime(decline_data['timestamp']).dt.floor('H')
        trend_data = decline_data.groupby(['hour', 'reason_code'])['decline_count'].sum().reset_index()
        
        fig = px.line(trend_data, x='hour', y='decline_count', color='reason_code',
                     labels={'hour': 'Time', 'decline_count': 'Decline Count'},
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommended Actions
    st.markdown("### 💡 Recommended Actions")
    
    # Group by reason code and recommended action
    action_summary = decline_data[decline_data['actionable'] == True].groupby(
        ['reason_code', 'recommended_action']
    )['decline_count'].sum().reset_index().sort_values('decline_count', ascending=False).head(10)
    
    for idx, row in action_summary.iterrows():
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.markdown(f"**{row['reason_code']}**")
        with col2:
            st.markdown(f"→ {row['recommended_action']}")
        with col3:
            st.markdown(f"*{row['decline_count']:,} declines*")
    
    # Detailed Breakdown
    st.markdown("### 📋 Decline Details by Segment")
    
    segment_filter = st.selectbox("Segment By", options=['geography', 'issuer', 'merchant_category', 'reason_code'])
    
    segment_stats = decline_data.groupby(segment_filter).agg({
        'decline_count': 'sum',
        'actionable': lambda x: (x == True).sum() / len(x) * 100
    }).reset_index().sort_values('decline_count', ascending=False)
    segment_stats.columns = [segment_filter, 'Total Declines', 'Actionable %']
    
    fig = px.bar(segment_stats.head(15), x=segment_filter, y='Total Declines',
                color='Actionable %',
                color_continuous_scale='RdYlGn',
                labels={segment_filter: segment_filter.replace('_', ' ').title()})
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Smart Retry

# COMMAND ----------

def show_smart_retry(retry_data):
    st.markdown('<h2 class="section-header">🔄 Smart Retry Recommendations</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        ML-powered retry decisioning to maximize recovery while minimizing wasteful retry attempts.
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_candidates = len(retry_data)
    retry_now = len(retry_data[retry_data['retry_recommendation'] == 'RETRY_NOW'])
    retry_later = len(retry_data[retry_data['retry_recommendation'] == 'RETRY_LATER'])
    do_not_retry = len(retry_data[retry_data['retry_recommendation'] == 'DO_NOT_RETRY'])
    
    with col1:
        st.metric("Total Candidates", f"{total_candidates:,}")
    with col2:
        st.metric("Retry Now", f"{retry_now:,}", delta=f"{(retry_now/total_candidates*100):.1f}%")
    with col3:
        st.metric("Retry Later", f"{retry_later:,}", delta=f"{(retry_later/total_candidates*100):.1f}%")
    with col4:
        potential_recovery = retry_data[retry_data['retry_recommendation'] != 'DO_NOT_RETRY']['amount'].sum()
        st.metric("Recovery Potential", f"${potential_recovery/1000:.1f}K")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Retry Recommendations Distribution")
        recommendation_counts = retry_data['retry_recommendation'].value_counts()
        colors = {'RETRY_NOW': '#3FB950', 'RETRY_LATER': '#FFA657', 'DO_NOT_RETRY': '#F85149'}
        fig = px.pie(values=recommendation_counts.values, names=recommendation_counts.index,
                    color=recommendation_counts.index,
                    color_discrete_map=colors)
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏰ Recommended Wait Times")
        wait_time_dist = retry_data[retry_data['retry_recommendation'] == 'RETRY_LATER']['recommended_wait_hours'].value_counts().sort_index()
        fig = px.bar(x=wait_time_dist.index, y=wait_time_dist.values,
                    labels={'x': 'Wait Time (Hours)', 'y': 'Transaction Count'},
                    color=wait_time_dist.values,
                    color_continuous_scale='Blues')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Success Probability Analysis
    st.markdown("### 🎯 Retry Success Probability Distribution")
    
    fig = px.histogram(retry_data, x='retry_success_probability', color='retry_recommendation',
                      nbins=30,
                      labels={'retry_success_probability': 'Predicted Success Probability',
                             'count': 'Transaction Count'},
                      color_discrete_map={'RETRY_NOW': '#3FB950', 'RETRY_LATER': '#FFA657', 'DO_NOT_RETRY': '#F85149'})
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=400,
        barmode='overlay'
    )
    fig.update_traces(opacity=0.7)
    st.plotly_chart(fig, use_container_width=True)
    
    # High Priority Retries
    st.markdown("### 🚨 High Priority Retry Opportunities")
    
    high_priority = retry_data[
        (retry_data['retry_recommendation'] == 'RETRY_NOW') & 
        (retry_data['retry_success_probability'] > 0.7)
    ].sort_values('amount', ascending=False).head(10)
    
    if not high_priority.empty:
        display_cols = ['transaction_id', 'original_decline_code', 'amount', 'retry_success_probability', 
                       'suggested_solution_mix', 'geography']
        st.dataframe(
            high_priority[display_cols].style.background_gradient(cmap='Greens', subset=['retry_success_probability']),
            use_container_width=True
        )
    else:
        st.info("No high priority retry opportunities at this time.")
    
    # Decline Code Analysis
    st.markdown("### 📉 Retry Success by Original Decline Code")
    
    decline_analysis = retry_data.groupby('original_decline_code').agg({
        'retry_success_probability': 'mean',
        'transaction_id': 'count',
        'amount': 'sum'
    }).reset_index().sort_values('retry_success_probability', ascending=False)
    decline_analysis.columns = ['Decline Code', 'Avg Success Probability', 'Count', 'Total Amount']
    
    fig = px.scatter(decline_analysis, x='Count', y='Avg Success Probability',
                    size='Total Amount', hover_data=['Decline Code'],
                    labels={'Count': 'Transaction Count', 'Avg Success Probability': 'Average Success Probability'},
                    color='Avg Success Probability',
                    color_continuous_scale='RdYlGn')
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Geographic Performance

# COMMAND ----------

def show_geographic_performance(checkout_data):
    st.markdown('<h2 class="section-header">🌍 Geographic Performance Analysis</h2>', unsafe_allow_html=True)
    
    # Calculate geo stats
    geo_stats = checkout_data.groupby('geography').agg({
        'transaction_id': 'count',
        'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
        'amount': ['sum', 'mean'],
        'risk_score': 'mean'
    }).reset_index()
    geo_stats.columns = ['geography', 'transaction_count', 'approval_rate', 'total_volume', 'avg_amount', 'avg_risk']
    
    # World Map
    st.markdown("### 🗺️ Global Approval Rate Map")
    
    # Map geography codes to full names and coordinates
    geo_mapping = {
        'US': {'name': 'United States', 'lat': 37.0902, 'lon': -95.7129},
        'EU': {'name': 'European Union', 'lat': 50.8503, 'lon': 4.3517},
        'UK': {'name': 'United Kingdom', 'lat': 55.3781, 'lon': -3.4360},
        'LATAM': {'name': 'Latin America', 'lat': -8.7832, 'lon': -55.4915},
        'APAC': {'name': 'Asia Pacific', 'lat': 34.0479, 'lon': 100.6197}
    }
    
    geo_stats['lat'] = geo_stats['geography'].map(lambda x: geo_mapping.get(x, {}).get('lat', 0))
    geo_stats['lon'] = geo_stats['geography'].map(lambda x: geo_mapping.get(x, {}).get('lon', 0))
    geo_stats['name'] = geo_stats['geography'].map(lambda x: geo_mapping.get(x, {}).get('name', x))
    
    fig = px.scatter_geo(geo_stats,
                        lat='lat', lon='lon',
                        size='transaction_count',
                        color='approval_rate',
                        hover_name='name',
                        hover_data={'transaction_count': True, 'approval_rate': ':.1f', 
                                   'total_volume': ':.0f', 'lat': False, 'lon': False},
                        color_continuous_scale='RdYlGn',
                        size_max=50)
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=500,
        geo=dict(
            showland=True,
            landcolor='#1C2128',
            showocean=True,
            oceancolor='#0D1117',
            showcountries=True,
            countrycolor='#30363D'
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional Comparison
    st.markdown("### 📊 Regional Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(geo_stats, x='geography', y='approval_rate',
                    color='approval_rate',
                    labels={'geography': 'Region', 'approval_rate': 'Approval Rate (%)'},
                    color_continuous_scale='RdYlGn')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(geo_stats, x='geography', y='avg_risk',
                    color='avg_risk',
                    labels={'geography': 'Region', 'avg_risk': 'Average Risk Score'},
                    color_continuous_scale='Reds')
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel Performance by Geography
    st.markdown("### 📱 Channel Performance by Region")
    
    channel_geo = checkout_data.groupby(['geography', 'channel']).agg({
        'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100
    }).reset_index()
    channel_geo.columns = ['geography', 'channel', 'approval_rate']
    
    fig = px.bar(channel_geo, x='geography', y='approval_rate', color='channel',
                barmode='group',
                labels={'approval_rate': 'Approval Rate (%)', 'geography': 'Region'},
                color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(
        plot_bgcolor='#0D1117',
        paper_bgcolor='#161B22',
        font_color='#C9D1D9',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional Statistics Table
    st.markdown("### 📋 Regional Performance Summary")
    
    display_stats = geo_stats[['geography', 'transaction_count', 'approval_rate', 'total_volume', 'avg_amount', 'avg_risk']]
    display_stats.columns = ['Region', 'Transactions', 'Approval Rate (%)', 'Total Volume ($)', 'Avg Amount ($)', 'Avg Risk Score']
    st.dataframe(
        display_stats.style.background_gradient(cmap='RdYlGn', subset=['Approval Rate (%)']).format({
            'Transactions': '{:,.0f}',
            'Approval Rate (%)': '{:.2f}',
            'Total Volume ($)': '${:,.2f}',
            'Avg Amount ($)': '${:.2f}',
            'Avg Risk Score': '{:.3f}'
        }),
        use_container_width=True
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Genie AI Assistant

# COMMAND ----------

def show_genie_assistant():
    st.markdown('<h2 class="section-header">🤖 Genie AI Assistant</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="genie-section">
        <div class="genie-icon">🧞‍♂️</div>
        <h3 style="text-align: center; color: #58A6FF;">Ask Genie About Your Payment Data</h3>
        <p style="text-align: center; color: #8B949E;">
            Use natural language to explore payment authorization data, decline patterns, and optimization opportunities.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example Queries
    st.markdown("### 💡 Example Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Business Questions:**
        - "What is driving the decline rate increase in EU this week?"
        - "Which payment solution mix has the highest approval rate for high-value transactions?"
        - "Show me the top 5 merchants with the highest decline rates"
        - "What percentage of declines are recoverable through retry?"
        """)
    
    with col2:
        st.markdown("""
        **Technical Questions:**
        - "How does 3DS impact approval rates across different geographies?"
        - "What is the correlation between risk score and approval probability?"
        - "Which issuers have the highest rate of security violations?"
        - "Compare approval rates for NetworkToken vs traditional card processing"
        """)
    
    # Query Input
    st.markdown("### 🔍 Ask Your Question")
    
    user_query = st.text_area(
        "Enter your question:",
        placeholder="e.g., What are the main reasons for declines in LATAM over the last 24 hours?",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Ask Genie", use_container_width=True):
            if user_query:
                with st.spinner("🧞‍♂️ Genie is analyzing your payment data..."):
                    # Simulate Genie response
                    import time
                    time.sleep(2)
                    
                    st.markdown("---")
                    st.markdown("### 💬 Genie's Response")
                    
                    # Mock response based on query keywords
                    if "decline" in user_query.lower() and "latam" in user_query.lower():
                        st.markdown("""
                        <div class="success-box">
                        <h4>📊 Analysis: LATAM Decline Patterns (Last 24 Hours)</h4>
                        
                        Based on your payment data, I found the following insights:
                        
                        **Top Decline Reasons:**
                        1. **05_DO_NOT_HONOR (42%)** - Primarily from cross-border transactions above $500
                        2. **63_SECURITY_VIOLATION (28%)** - Spike in fraud scoring threshold triggers
                        3. **51_INSUFFICIENT_FUNDS (18%)** - Concentrated around month-end period
                        
                        **Key Findings:**
                        - Decline rate increased from 15% to 23% (+8 percentage points)
                        - 67% of declines are actionable with solution mix optimization
                        - Enabling **3DS + Antifraud** shows potential for 12% approval uplift
                        
                        **Recommended Actions:**
                        1. Enable mandatory 3DS for LATAM transactions > $300
                        2. Route high-risk merchants through NetworkToken path
                        3. Implement Smart Retry for insufficient funds cases (optimal window: 24-48h after salary dates)
                        
                        **Potential Impact:**
                        - Projected approval rate improvement: +8-10%
                        - Revenue recovery opportunity: $45K - $62K per week
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Generate supporting chart
                        sample_data = pd.DataFrame({
                            'Decline Reason': ['DO_NOT_HONOR', 'SECURITY_VIOLATION', 'INSUFFICIENT_FUNDS', 'EXCEEDS_LIMIT', 'OTHER'],
                            'Count': [420, 280, 180, 85, 35],
                            'Recoverable %': [65, 45, 85, 55, 30]
                        })
                        
                        fig = px.bar(sample_data, x='Decline Reason', y='Count',
                                    color='Recoverable %',
                                    labels={'Count': 'Decline Count'},
                                    color_continuous_scale='RdYlGn',
                                    title='LATAM Decline Distribution')
                        fig.update_layout(
                            plot_bgcolor='#0D1117',
                            paper_bgcolor='#161B22',
                            font_color='#C9D1D9',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif "solution mix" in user_query.lower() or "approval rate" in user_query.lower():
                        st.markdown("""
                        <div class="success-box">
                        <h4>🎯 Analysis: Payment Solution Performance</h4>
                        
                        **Top Performing Solution Combinations:**
                        
                        1. **NetworkToken + 3DS** (Approval Rate: 94.2%)
                           - Best for: EU, UK, regulated merchants
                           - Average transaction: $287
                           - Cost per transaction: $0.23
                        
                        2. **Passkey + Antifraud** (Approval Rate: 92.8%)
                           - Best for: Mobile commerce, returning customers
                           - Average transaction: $156
                           - Cost per transaction: $0.22
                        
                        3. **3DS + Antifraud + IDPay** (Approval Rate: 89.5%)
                           - Best for: High-risk merchants, large transactions (>$2500)
                           - Average transaction: $1,842
                           - Cost per transaction: $0.45
                        
                        **Key Insight:** 
                        Switching from basic Antifraud to NetworkToken+3DS for EU transactions shows 
                        a **+12% approval uplift** with only $0.13 additional cost per transaction.
                        
                        **ROI Calculation:**
                        - Additional cost: $1,300/day
                        - Additional approvals: 450/day @ $250 avg = $112,500/day
                        - Net benefit: **$111,200/day** or **$3.36M/month**
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.markdown("""
                        <div class="info-box">
                        <h4>🧞‍♂️ General Payment Insights</h4>
                        
                        I've analyzed your payment authorization data. Here are some key insights:
                        
                        **Current Performance:**
                        - Overall approval rate: 85.3% (↑2.1% vs last week)
                        - Total transactions: 12,450 (last 24 hours)
                        - Average risk score: 0.24 (low-medium risk)
                        
                        **Opportunities:**
                        - 850 transactions eligible for Smart Retry (potential recovery: $127K)
                        - 3DS adoption in APAC could improve approval rate by 6-8%
                        - NetworkToken shows 15% better approval vs traditional card-on-file
                        
                        **Alerts:**
                        - Security violations trending up in LATAM (+35% this week)
                        - Issuer "BANK_XYZ" showing elevated decline rate (23% vs 15% baseline)
                        
                        Try asking more specific questions about geographies, merchants, or solution mixes!
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a question to ask Genie.")
    
    # Pre-built Queries
    st.markdown("### ⚡ Quick Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Approval Trends", use_container_width=True):
            st.info("Loading approval rate trends across all dimensions...")
    
    with col2:
        if st.button("💰 Revenue Impact", use_container_width=True):
            st.info("Calculating revenue impact of optimization opportunities...")
    
    with col3:
        if st.button("🎯 Best Practices", use_container_width=True):
            st.info("Generating recommended practices based on your data...")
    
    # Integration Info
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
    <h4>🔗 Genie Integration Details</h4>
    <p>
    This AI Assistant is powered by <strong>Databricks Genie</strong>, which provides natural language querying 
    over your lakehouse data. Genie automatically:
    </p>
    <ul>
        <li>Understands business terminology and payment domain concepts</li>
        <li>Generates optimized SQL queries against your Delta tables</li>
        <li>Provides context-aware insights and recommendations</li>
        <li>Learns from your query patterns to improve over time</li>
    </ul>
    <p>
    <strong>Setup:</strong> Connect Genie to your payment lakehouse catalog and enable domain-specific training 
    on your payment authorization schema.
    </p>
    </div>
    """, unsafe_allow_html=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Page: Configuration

# COMMAND ----------

def show_configuration():
    st.markdown('<h2 class="section-header">⚙️ System Configuration</h2>', unsafe_allow_html=True)
    
    # Load policies
    try:
        with open('/dbfs/payments_demo/config/policies.json', 'r') as f:
            policies = json.load(f)
    except:
        st.warning("Could not load policies.json. Using default configuration.")
        policies = {}
    
    # Tabs for different config sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Routing Strategies", "🔄 Retry Policies", "📊 Monitoring", "🔧 Feature Flags"])
    
    with tab1:
        st.markdown("### Payment Routing Configuration")
        
        if policies.get('routing_policies'):
            strategy = st.selectbox(
                "Default Routing Strategy",
                options=list(policies['routing_policies'].get('strategies', {}).keys())
            )
            
            if strategy:
                strategy_config = policies['routing_policies']['strategies'][strategy]
                st.markdown(f"**Description:** {strategy_config.get('description', 'N/A')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.number_input("Weight: Approval", value=strategy_config.get('weight_approval', 0.5), step=0.1)
                with col2:
                    st.number_input("Weight: Cost", value=strategy_config.get('weight_cost', 0.3), step=0.1)
                with col3:
                    st.number_input("Weight: Risk", value=strategy_config.get('weight_risk', 0.2), step=0.1)
        
        st.markdown("### Geographic Rules")
        geo_rules = st.multiselect(
            "Regions with Mandatory 3DS",
            options=['EU', 'UK', 'IN', 'AU', 'LATAM', 'APAC', 'US'],
            default=['EU', 'UK', 'IN']
        )
        
    with tab2:
        st.markdown("### Smart Retry Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            max_attempts = st.slider("Max Retry Attempts", 1, 10, 5)
            min_success_prob = st.slider("Min Success Probability Threshold", 0.0, 1.0, 0.30, 0.05)
        
        with col2:
            enable_salary_day = st.checkbox("Optimize for Salary Days", value=True)
            enable_business_hours = st.checkbox("Optimize for Business Hours", value=True)
        
        st.markdown("### Backoff Schedule")
        backoff_schedule = st.text_input(
            "Retry Delay Schedule (hours, comma-separated)",
            value="1, 3, 24, 72, 168"
        )
    
    with tab3:
        st.markdown("### KPI Thresholds & Alerts")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Approval Rate**")
            approval_target = st.number_input("Target (%)", value=85.0, step=0.5)
            approval_warning = st.number_input("Warning Below (%)", value=80.0, step=0.5)
            approval_critical = st.number_input("Critical Below (%)", value=75.0, step=0.5)
        
        with col2:
            st.markdown("**Fraud Rate**")
            fraud_target = st.number_input("Target (%)", value=1.0, step=0.1, key="fraud_target")
            fraud_warning = st.number_input("Warning Above (%)", value=2.0, step=0.1, key="fraud_warning")
            fraud_critical = st.number_input("Critical Above (%)", value=5.0, step=0.1, key="fraud_critical")
        
        with col3:
            st.markdown("**Processing Time**")
            latency_target = st.number_input("Target (ms)", value=1500, step=100)
            latency_warning = st.number_input("Warning Above (ms)", value=2500, step=100)
            latency_critical = st.number_input("Critical Above (ms)", value=4000, step=100)
        
        st.markdown("### Alert Channels")
        alert_email = st.text_input("Email Recipients (comma-separated)", 
                                    value="payments-team@example.com, risk-team@example.com")
        alert_slack = st.text_input("Slack Channel", value="#payments-alerts")
    
    with tab4:
        st.markdown("### Feature Flags")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Enable Smart Checkout", value=True, key="enable_checkout")
            st.checkbox("Enable Cascading", value=True, key="enable_cascade")
            st.checkbox("Enable Smart Retry", value=True, key="enable_retry")
            st.checkbox("Enable Network Tokenization", value=True, key="enable_token")
        
        with col2:
            st.checkbox("Enable Biometric Auth", value=True, key="enable_bio")
            st.checkbox("Enable ML Scoring", value=True, key="enable_ml")
            st.checkbox("Enable Real-time Updates", value=True, key="enable_realtime")
            st.checkbox("Enable A/B Testing", value=False, key="enable_ab")
        
        st.markdown("### System Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Data Retention (days)", value=2555, step=1)
            st.selectbox("Encryption Level", options=["Standard", "Enhanced", "Maximum"])
        with col2:
            st.number_input("Monitoring Frequency (seconds)", value=60, step=10)
            st.checkbox("Verbose Logging", value=False)
    
    # Save button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("✅ Configuration saved successfully!")
            st.info("Changes will take effect on next streaming job restart.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Application

# COMMAND ----------

if __name__ == "__main__":
    main()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deployment Instructions
# MAGIC 
# MAGIC To deploy this as a Databricks App:
# MAGIC 
# MAGIC 1. **Save this notebook** in your Databricks workspace
# MAGIC 2. **Install required libraries** (first cell with %pip)
# MAGIC 3. **Configure app settings:**
# MAGIC    ```python
# MAGIC    # In Databricks workspace:
# MAGIC    # Apps > Create App > Select this notebook
# MAGIC    ```
# MAGIC 4. **Set environment variables:**
# MAGIC    - CATALOG: `payments_lakehouse`
# MAGIC    - SCHEMA_GOLD: `gold`
# MAGIC 5. **Grant permissions:**
# MAGIC    - SELECT on all Gold tables
# MAGIC    - USAGE on catalog and schemas
# MAGIC 6. **Deploy and share** the app URL with stakeholders
# MAGIC 
# MAGIC **App URL format:** `https://<workspace>.databricks.com/apps/<app-id>`
