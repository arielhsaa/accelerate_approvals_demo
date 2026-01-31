import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import json
import pydeck as pdk

# Set page config - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Payment Authorization Command Center",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.databricks.com',
        'Report a bug': None,
        'About': "Payment Authorization Command Center v2.0 - Powered by Databricks"
    }
)




# Premium CSS with enhanced styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root variables - Premium color palette */
    :root {
        --primary-color: #FF3621;
        --primary-dark: #CC2B1A;
        --secondary-color: #00A972;
        --accent-color: #58A6FF;
        --success-color: #3FB950;
        --warning-color: #D29922;
        --danger-color: #F85149;
        --background-dark: #0D1117;
        --background-darker: #010409;
        --card-background: #161B22;
        --card-background-hover: #1C2128;
        --text-primary: #E6EDF3;
        --text-secondary: #8B949E;
        --text-muted: #6E7681;
        --border-color: #30363D;
        --border-color-hover: #484F58;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.16);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.25);
    }
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: var(--background-dark);
    }
    
    /* Premium header with gradient */
    .premium-header {
        background: linear-gradient(135deg, #FF3621 0%, #FF8A00 50%, #FFC837 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,138.7C960,139,1056,117,1152,101.3C1248,85,1344,75,1392,69.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
        background-size: cover;
        opacity: 0.3;
    }
    
    .premium-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        margin-top: 0.75rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    .premium-header .status-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced KPI Cards */
    .kpi-card-premium {
        background: linear-gradient(135deg, var(--card-background) 0%, var(--card-background-hover) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent-color) 0%, var(--primary-color) 100%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .kpi-card-premium:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--border-color-hover);
    }
    
    .kpi-card-premium:hover::before {
        opacity: 1;
    }
    
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    }
    
    .kpi-value-premium {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .kpi-label-premium {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .kpi-delta-positive {
        color: var(--success-color);
        font-size: 1.1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .kpi-delta-negative {
        color: var(--danger-color);
        font-size: 1.1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .kpi-delta-neutral {
        color: var(--text-muted);
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    /* Section headers with icons */
    .section-header-premium {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header-premium::before {
        content: '';
        width: 6px;
        height: 40px;
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--accent-color) 100%);
        border-radius: 3px;
    }
    
    /* Enhanced metric cards */
    .metric-card-premium {
        background: var(--card-background);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s;
    }
    
    .metric-card-premium:hover {
        box-shadow: var(--shadow-md);
        border-left-color: var(--primary-color);
    }
    
    /* Info boxes with enhanced styling */
    .info-box-premium {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(88, 166, 255, 0.05) 100%);
        border: 1px solid rgba(88, 166, 255, 0.3);
        border-left: 4px solid var(--accent-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .success-box-premium {
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.1) 0%, rgba(63, 185, 80, 0.05) 100%);
        border: 1px solid rgba(63, 185, 80, 0.3);
        border-left: 4px solid var(--success-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .warning-box-premium {
        background: linear-gradient(135deg, rgba(210, 153, 34, 0.1) 0%, rgba(210, 153, 34, 0.05) 100%);
        border: 1px solid rgba(210, 153, 34, 0.3);
        border-left: 4px solid var(--warning-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .danger-box-premium {
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.1) 0%, rgba(248, 81, 73, 0.05) 100%);
        border: 1px solid rgba(248, 81, 73, 0.3);
        border-left: 4px solid var(--danger-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Country cards for geo analytics */
    .country-card {
        background: var(--card-background);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .country-card:hover {
        border-color: var(--accent-color);
        transform: translateX(4px);
        box-shadow: var(--shadow-md);
    }
    
    .country-flag {
        font-size: 2rem;
        margin-right: 0.75rem;
    }
    
    .country-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .country-stats {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.75rem;
        font-size: 0.9rem;
    }
    
    .country-stat-item {
        display: flex;
        flex-direction: column;
    }
    
    .country-stat-label {
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .country-stat-value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Filters and controls */
    .filter-container {
        background: var(--card-background);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Data table styling */
    .dataframe {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
    
    .dataframe th {
        background: var(--card-background) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .dataframe td {
        padding: 0.75rem !important;
        border-color: var(--border-color) !important;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: var(--card-background);
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    /* Plotly chart containers */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-live {
        background: rgba(63, 185, 80, 0.2);
        color: var(--success-color);
        border: 1px solid var(--success-color);
    }
    
    .status-processing {
        background: rgba(210, 153, 34, 0.2);
        color: var(--warning-color);
        border: 1px solid var(--warning-color);
    }
    
    /* Tooltips */
    .tooltip-custom {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    /* Animation keyframes */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .premium-header h1 {
            font-size: 2rem;
        }
        
        .kpi-value-premium {
            font-size: 2rem;
        }
        
        .section-header-premium {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)




@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_delta(table_name, limit=10000):
    """Load data from Delta table with caching"""
    try:
        # Try to connect to Databricks
        from databricks import sql
        import os
        
        # In Databricks environment, connection is automatic
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = spark.sql(query).toPandas()
        return df
    except Exception as e:
        # Fallback to synthetic data for demo/local testing
        st.warning(f"Using synthetic data for demonstration. Error: {str(e)}")
        return generate_synthetic_data(table_name)

@st.cache_data(ttl=60)  # Cache for 1 minute for real-time feel
def generate_synthetic_data(table_type):
    """Generate realistic synthetic data for different table types"""
    np.random.seed(42)
    
    if table_type == 'payments_enriched_stream' or 'checkout' in table_type:
        n = 5000
        countries = ['USA', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Brazil', 'Mexico', 'Canada', 'Australia', 
                    'Japan', 'India', 'China', 'Singapore', 'Netherlands', 'Belgium', 'Sweden', 'Norway']
        
        # Generate country data with realistic distribution
        country_weights = [0.25, 0.15, 0.10, 0.08, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03,
                          0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01]
        
        df = pd.DataFrame({
            'transaction_id': [f'TXN{str(i).zfill(8)}' for i in range(1, n+1)],
            'timestamp': pd.date_range(end=datetime.now(), periods=n, freq='30S'),
            'amount': np.random.lognormal(5, 1.5, n).round(2),
            'geography': np.random.choice(countries, n, p=country_weights),
            'country_code': np.random.choice(['US', 'GB', 'DE', 'FR', 'ES', 'IT', 'BR', 'MX', 'CA', 'AU',
                                             'JP', 'IN', 'CN', 'SG', 'NL', 'BE', 'SE', 'NO'], n, p=country_weights),
            'channel': np.random.choice(['ecommerce', 'pos', 'moto', 'recurring'], n, p=[0.5, 0.3, 0.15, 0.05]),
            'card_network': np.random.choice(['VISA', 'MASTERCARD', 'AMEX', 'DISCOVER'], n, p=[0.5, 0.3, 0.15, 0.05]),
            'approval_status': np.random.choice(['approved', 'declined'], n, p=[0.88, 0.12]),
            'risk_score': np.random.beta(2, 5, n).round(3),
            'recommended_solution_name': np.random.choice([
                '3DS+Antifraud', 'NetworkToken+3DS', 'IDPay+3DS', 'Antifraud Only', 
                'Full Stack', 'Baseline', '3DS Only', 'NetworkToken Only'
            ], n),
            'has_3ds': np.random.choice([True, False], n, p=[0.7, 0.3]),
            'has_antifraud': np.random.choice([True, False], n, p=[0.6, 0.4]),
            'has_network_token': np.random.choice([True, False], n, p=[0.5, 0.5]),
            'issuer_country': np.random.choice(countries, n, p=country_weights),
            'merchant_category': np.random.choice(['retail', 'travel', 'digital_goods', 'services', 'gaming'], n),
            'is_cross_border': np.random.choice([True, False], n, p=[0.3, 0.7])
        })
        
        # Add lat/lon for geo visualization
        country_coords = {
            'USA': (37.0902, -95.7129), 'UK': (55.3781, -3.4360), 'Germany': (51.1657, 10.4515),
            'France': (46.2276, 2.2137), 'Spain': (40.4637, -3.7492), 'Italy': (41.8719, 12.5674),
            'Brazil': (-14.2350, -51.9253), 'Mexico': (23.6345, -102.5528), 'Canada': (56.1304, -106.3468),
            'Australia': (-25.2744, 133.7751), 'Japan': (36.2048, 138.2529), 'India': (20.5937, 78.9629),
            'China': (35.8617, 104.1954), 'Singapore': (1.3521, 103.8198), 'Netherlands': (52.1326, 5.2913),
            'Belgium': (50.5039, 4.4699), 'Sweden': (60.1282, 18.6435), 'Norway': (60.4720, 8.4689)
        }
        
        df['latitude'] = df['geography'].map(lambda x: country_coords.get(x, (0, 0))[0])
        df['longitude'] = df['geography'].map(lambda x: country_coords.get(x, (0, 0))[1])
        
        return df
    
    elif 'decline' in table_type or 'reason' in table_type:
        n = 800
        reason_codes = [
            '05_DO_NOT_HONOR', '51_INSUFFICIENT_FUNDS', '63_SECURITY_VIOLATION',
            '14_INVALID_CARD', '54_EXPIRED_CARD', '04_PICK_UP_CARD',
            '41_LOST_CARD', '43_STOLEN_CARD', '61_EXCEEDS_LIMIT',
            '91_ISSUER_UNAVAILABLE', '96_SYSTEM_MALFUNCTION', '12_INVALID_TRANSACTION'
        ]
        
        df = pd.DataFrame({
            'reason_code': np.random.choice(reason_codes, n),
            'decline_count': np.random.randint(1, 500, n),
            'geography': np.random.choice(['USA', 'UK', 'Germany', 'France', 'Spain', 'Brazil', 'Mexico'], n),
            'issuer': np.random.choice([f'Issuer_{i}' for i in range(1, 21)], n),
            'severity': np.random.choice(['low', 'medium', 'high', 'critical'], n, p=[0.3, 0.4, 0.2, 0.1])
        })
        
        return df
    
    elif 'retry' in table_type:
        n = 1200
        df = pd.DataFrame({
            'transaction_id': [f'TXN{str(i).zfill(8)}' for i in range(1, n+1)],
            'retry_recommendation': np.random.choice(['RETRY_NOW', 'RETRY_LATER', 'DO_NOT_RETRY'], n, p=[0.3, 0.5, 0.2]),
            'retry_success_probability': np.random.beta(3, 2, n).round(3),
            'optimal_retry_window_hours': np.random.choice([2, 4, 8, 12, 24, 48], n),
            'expected_recovery_amount': np.random.lognormal(4.5, 1, n).round(2),
            'geography': np.random.choice(['USA', 'UK', 'Germany', 'France', 'Spain', 'Brazil'], n),
            'risk_score': np.random.beta(2, 5, n).round(3)
        })
        
        return df
    
    else:
        # Generic data
        return pd.DataFrame({
            'id': range(100),
            'value': np.random.randn(100)
        })




def show_premium_header():
    """Display premium header with live status"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.markdown(f"""
    <div class="premium-header">
        <h1>💳 Payment Authorization Command Center</h1>
        <p>Real-time global payment intelligence powered by Databricks Lakehouse</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
            <span class="status-badge">
                <span class="pulse" style="color: #3FB950;">●</span> Live Streaming
            </span>
            <span class="status-badge">
                🌍 18 Countries
            </span>
            <span class="status-badge">
                📊 5,000+ Transactions/min
            </span>
            <span class="status-badge">
                ⏱️ Last Updated: {current_time}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)




def main():
    """Main application with enhanced navigation"""
    
    # Show premium header
    show_premium_header()
    
    # Sidebar navigation with icons
    with st.sidebar:
        st.image("https://www.databricks.com/wp-content/uploads/2021/06/db-nav-logo.svg", width=180)
        st.markdown("---")
        
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "🏠 Executive Dashboard",
                "🗺️ Global Geo-Analytics",
                "🎯 Smart Checkout",
                "📉 Decline Analysis",
                "🔄 Smart Retry",
                "📊 Performance Metrics",
                "🤖 Genie AI Assistant",
                "⚙️ Settings & Config"
            ],
            icons=['house', 'globe', 'bullseye', 'graph-down', 'arrow-repeat', 'bar-chart', 'robot', 'gear'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0.5rem", "background-color": "#161B22"},
                "icon": {"color": "#58A6FF", "font-size": "1.2rem"},
                "nav-link": {
                    "font-size": "0.95rem",
                    "text-align": "left",
                    "margin": "0.25rem 0",
                    "padding": "0.75rem 1rem",
                    "border-radius": "8px",
                    "--hover-color": "#1C2128",
                },
                "nav-link-selected": {
                    "background-color": "#FF3621",
                    "color": "white",
                    "font-weight": "600"
                },
            }
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        st.markdown("### 📈 Quick Stats")
        st.metric("Approval Rate", "92.3%", "+7.8%")
        st.metric("Active Countries", "18", "+2")
        st.metric("ML Model Accuracy", "94.5%", "+1.2%")
        
        st.markdown("---")
        st.markdown("**Version:** 2.0 Premium")
        st.markdown("**Build:** 2026-01-31")
    
    # Load data once
    checkout_data = load_data_from_delta('payments_lakehouse.silver.payments_enriched_stream')
    decline_data = load_data_from_delta('payments_lakehouse.gold.decline_distribution')
    retry_data = load_data_from_delta('payments_lakehouse.gold.smart_retry_recommendations')
    
    # Route to selected page
    if selected == "🏠 Executive Dashboard":
        show_executive_dashboard(checkout_data, decline_data, retry_data)
    elif selected == "🗺️ Global Geo-Analytics":
        show_global_geo_analytics(checkout_data)
    elif selected == "🎯 Smart Checkout":
        show_smart_checkout(checkout_data)
    elif selected == "📉 Decline Analysis":
        show_decline_analysis(decline_data, checkout_data)
    elif selected == "🔄 Smart Retry":
        show_smart_retry(retry_data)
    elif selected == "📊 Performance Metrics":
        show_performance_metrics(checkout_data, decline_data, retry_data)
    elif selected == "🤖 Genie AI Assistant":
        show_genie_assistant()
    elif selected == "⚙️ Settings & Config":
        show_settings()




def show_executive_dashboard(checkout_data, decline_data, retry_data):
    """Premium executive dashboard with key metrics"""
    
    st.markdown('<h2 class="section-header-premium">📊 Executive Overview</h2>', unsafe_allow_html=True)
    
    # Calculate KPIs
    if not checkout_data.empty:
        total_transactions = len(checkout_data)
        approved = checkout_data[checkout_data['approval_status'] == 'approved']
        approval_rate = (len(approved) / total_transactions * 100) if total_transactions > 0 else 0
        total_volume = approved['amount'].sum() if 'amount' in approved.columns else 0
        avg_risk = checkout_data['risk_score'].mean() if 'risk_score' in checkout_data.columns else 0
        
        # Calculate deltas (simulated)
        approval_delta = 7.8
        volume_delta = 12.5
        risk_delta = -15.3
        transaction_delta = 8.2
    else:
        total_transactions = 0
        approval_rate = 0
        total_volume = 0
        avg_risk = 0
        approval_delta = 0
        volume_delta = 0
        risk_delta = 0
        transaction_delta = 0
    
    # Premium KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card-premium">
            <div class="kpi-icon">✅</div>
            <div class="kpi-label-premium">Approval Rate</div>
            <div class="kpi-value-premium">{approval_rate:.1f}%</div>
            <div class="kpi-delta-positive">
                ↑ +{approval_delta}% vs baseline
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card-premium">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label-premium">Approved Volume</div>
            <div class="kpi-value-premium">${total_volume/1e6:.2f}M</div>
            <div class="kpi-delta-positive">
                ↑ +{volume_delta}% vs last week
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card-premium">
            <div class="kpi-icon">🔒</div>
            <div class="kpi-label-premium">Avg Risk Score</div>
            <div class="kpi-value-premium">{avg_risk:.3f}</div>
            <div class="kpi-delta-positive">
                ↓ {risk_delta}% (Lower is better)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card-premium">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label-premium">Total Transactions</div>
            <div class="kpi-value-premium">{total_transactions:,}</div>
            <div class="kpi-delta-positive">
                ↑ +{transaction_delta}% growth
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Approval Trends Chart
    st.markdown('<h3 class="section-header-premium">📈 Approval Rate Trends (Last 7 Days)</h3>', unsafe_allow_html=True)
    
    if not checkout_data.empty and 'timestamp' in checkout_data.columns:
        # Resample by hour
        checkout_data['timestamp'] = pd.to_datetime(checkout_data['timestamp'])
        hourly_stats = checkout_data.set_index('timestamp').resample('1H').agg({
            'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
            'transaction_id': 'count'
        }).reset_index()
        hourly_stats.columns = ['timestamp', 'approval_rate', 'transaction_count']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=hourly_stats['timestamp'],
                y=hourly_stats['approval_rate'],
                name='Approval Rate',
                mode='lines+markers',
                line=dict(color='#3FB950', width=3),
                fill='tozeroy',
                fillcolor='rgba(63, 185, 80, 0.1)',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Bar(
                x=hourly_stats['timestamp'],
                y=hourly_stats['transaction_count'],
                name='Transaction Volume',
                marker_color='#58A6FF',
                opacity=0.3,
                hovertemplate='%{y} txns<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            plot_bgcolor='#0D1117',
            paper_bgcolor='#161B22',
            font_color='#C9D1D9',
            height=400,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
        fig.update_yaxes(title_text="Approval Rate (%)", secondary_y=False, showgrid=True, gridwidth=1, gridcolor='#30363D')
        fig.update_yaxes(title_text="Transaction Count", secondary_y=True, showgrid=False)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Global Performance and Insights
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h3 class="section-header-premium">🌍 Global Performance Overview</h3>', unsafe_allow_html=True)
        
        if not checkout_data.empty and 'geography' in checkout_data.columns:
            # Top countries
            country_stats = checkout_data.groupby('geography').agg({
                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
                'transaction_id': 'count',
                'amount': 'sum'
            }).reset_index()
            country_stats.columns = ['country', 'approval_rate', 'txn_count', 'volume']
            country_stats = country_stats.nlargest(10, 'txn_count')
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=country_stats['country'],
                y=country_stats['approval_rate'],
                name='Approval Rate (%)',
                marker_color='#3FB950',
                text=country_stats['approval_rate'].round(1),
                textposition='outside',
                texttemplate='%{text}%',
                hovertemplate='<b>%{x}</b><br>Approval Rate: %{y:.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=400,
                xaxis_title="Country",
                yaxis_title="Approval Rate (%)",
                showlegend=False
            )
            
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="section-header-premium">💡 Key Insights</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="success-box-premium">
            <h4>✅ Strong Performance</h4>
            <p><strong>EU Region:</strong> Approval rate up 12% with 3DS+NetworkToken combination</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box-premium">
            <h4>⚠️ Attention Needed</h4>
            <p><strong>LATAM:</strong> Security violations up 35% in last 6 hours</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box-premium">
            <h4>💰 Revenue Opportunity</h4>
            <p><strong>Smart Retry:</strong> 450 transactions with >70% retry success probability = $127K potential recovery</p>
        </div>
        """, unsafe_allow_html=True)




def show_global_geo_analytics(checkout_data):
    """Advanced geo-location analytics with interactive maps"""
    
    st.markdown('<h2 class="section-header-premium">🗺️ Global Geo-Location Analytics</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box-premium">
        <p><strong>Interactive geographic analysis</strong> of payment authorization performance across countries. 
        Click on countries for detailed drill-downs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if checkout_data.empty:
        st.warning("No data available for geo-analytics")
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        time_range = st.selectbox(
            "📅 Time Range",
            ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
            index=2
        )
    
    with col2:
        channel_filter = st.multiselect(
            "📱 Channel",
            options=['All'] + list(checkout_data['channel'].unique()) if 'channel' in checkout_data.columns else ['All'],
            default=['All']
        )
    
    with col3:
        min_transactions = st.slider(
            "Min Transactions",
            min_value=0,
            max_value=500,
            value=10,
            step=10
        )
    
    with col4:
        metric_view = st.selectbox(
            "🎯 Primary Metric",
            ["Approval Rate", "Transaction Volume", "Avg Transaction Value", "Risk Score"]
        )
    
    st.markdown("---")
    
    # Prepare geo data
    if 'geography' in checkout_data.columns and 'latitude' in checkout_data.columns:
        geo_data = checkout_data.groupby(['geography', 'latitude', 'longitude', 'country_code']).agg({
            'approval_status': [
                lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                'count'
            ],
            'amount': ['sum', 'mean'],
            'risk_score': 'mean'
        }).reset_index()
        
        geo_data.columns = ['country', 'lat', 'lon', 'country_code', 'approval_rate', 'txn_count', 'total_volume', 'avg_value', 'avg_risk']
        geo_data = geo_data[geo_data['txn_count'] >= min_transactions]
        
        # Tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Interactive Map", "🌍 Choropleth", "📊 Country Rankings", "🔍 Drill-Down"])
        
        with tab1:
            st.markdown("### Interactive Global Transaction Map")
            
            # Create bubble map with PyDeck
            if not geo_data.empty:
                # Normalize values for bubble size
                geo_data['size'] = (geo_data['txn_count'] / geo_data['txn_count'].max() * 1000000).fillna(0)
                geo_data['color'] = geo_data['approval_rate'].apply(
                    lambda x: [63, 185, 80, 200] if x >= 90 else 
                             [210, 153, 34, 200] if x >= 80 else 
                             [248, 81, 73, 200]
                )
                
                # Create PyDeck layer
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=geo_data,
                    get_position=['lon', 'lat'],
                    get_radius='size',
                    get_fill_color='color',
                    pickable=True,
                    opacity=0.6,
                    stroked=True,
                    filled=True,
                    radius_scale=1,
                    radius_min_pixels=5,
                    radius_max_pixels=100,
                    line_width_min_pixels=1,
                )
                
                # Set viewport
                view_state = pdk.ViewState(
                    latitude=20,
                    longitude=0,
                    zoom=1.5,
                    pitch=0,
                )
                
                # Create deck
                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={
                        "html": "<b>{country}</b><br/>"
                               "Approval Rate: {approval_rate:.1f}%<br/>"
                               "Transactions: {txn_count:,}<br/>"
                               "Volume: ${total_volume:,.0f}<br/>"
                               "Avg Value: ${avg_value:.2f}",
                        "style": {
                            "backgroundColor": "#161B22",
                            "color": "#E6EDF3",
                            "border": "1px solid #30363D",
                            "borderRadius": "8px",
                            "padding": "10px"
                        }
                    },
                    map_style='mapbox://styles/mapbox/dark-v10'
                )
                
                st.pydeck_chart(deck)
                
                # Legend
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<span style="color: #3FB950;">●</span> Approval Rate ≥ 90%', unsafe_allow_html=True)
                with col2:
                    st.markdown('<span style="color: #D29922;">●</span> Approval Rate 80-90%', unsafe_allow_html=True)
                with col3:
                    st.markdown('<span style="color: #F85149;">●</span> Approval Rate < 80%', unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### World Choropleth Map")
            
            if not geo_data.empty:
                # Create choropleth map
                fig = px.choropleth(
                    geo_data,
                    locations='country_code',
                    color='approval_rate',
                    hover_name='country',
                    hover_data={
                        'country_code': False,
                        'approval_rate': ':.1f',
                        'txn_count': ':,',
                        'total_volume': ':$,.0f',
                        'avg_risk': ':.3f'
                    },
                    color_continuous_scale=[
                        [0.0, '#F85149'],
                        [0.5, '#D29922'],
                        [1.0, '#3FB950']
                    ],
                    range_color=[0, 100],
                    labels={'approval_rate': 'Approval Rate (%)'}
                )
                
                fig.update_geos(
                    showcountries=True,
                    countrycolor="#30363D",
                    showcoastlines=True,
                    coastlinecolor="#30363D",
                    showland=True,
                    landcolor="#0D1117",
                    showocean=True,
                    oceancolor="#010409",
                    projection_type='natural earth',
                    bgcolor='#161B22'
                )
                
                fig.update_layout(
                    height=600,
                    paper_bgcolor='#161B22',
                    font_color='#C9D1D9',
                    geo=dict(bgcolor='#161B22'),
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### Country Performance Rankings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top Performers (Approval Rate)")
                top_performers = geo_data.nlargest(10, 'approval_rate')[['country', 'approval_rate', 'txn_count', 'total_volume']]
                
                for idx, row in top_performers.iterrows():
                    st.markdown(f"""
                    <div class="country-card">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span class="country-name">{row['country']}</span>
                                <div class="country-stats">
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Approval</span>
                                        <span class="country-stat-value" style="color: #3FB950;">{row['approval_rate']:.1f}%</span>
                                    </div>
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Volume</span>
                                        <span class="country-stat-value">{row['txn_count']:,}</span>
                                    </div>
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Value</span>
                                        <span class="country-stat-value">${row['total_volume']:,.0f}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📈 Highest Volume")
                top_volume = geo_data.nlargest(10, 'txn_count')[['country', 'approval_rate', 'txn_count', 'total_volume']]
                
                for idx, row in top_volume.iterrows():
                    approval_color = '#3FB950' if row['approval_rate'] >= 90 else '#D29922' if row['approval_rate'] >= 80 else '#F85149'
                    st.markdown(f"""
                    <div class="country-card">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span class="country-name">{row['country']}</span>
                                <div class="country-stats">
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Volume</span>
                                        <span class="country-stat-value">{row['txn_count']:,}</span>
                                    </div>
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Approval</span>
                                        <span class="country-stat-value" style="color: {approval_color};">{row['approval_rate']:.1f}%</span>
                                    </div>
                                    <div class="country-stat-item">
                                        <span class="country-stat-label">Value</span>
                                        <span class="country-stat-value">${row['total_volume']:,.0f}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown("### 🔍 Country Drill-Down Analysis")
            
            selected_country = st.selectbox(
                "Select Country for Detailed Analysis",
                options=sorted(geo_data['country'].unique())
            )
            
            if selected_country:
                country_data = checkout_data[checkout_data['geography'] == selected_country]
                
                if not country_data.empty:
                    # Country-specific KPIs
                    col1, col2, col3, col4 = st.columns(4)
                    
                    country_approval = (country_data['approval_status'] == 'approved').sum() / len(country_data) * 100
                    country_volume = country_data[country_data['approval_status'] == 'approved']['amount'].sum()
                    country_avg_risk = country_data['risk_score'].mean()
                    country_txns = len(country_data)
                    
                    with col1:
                        st.metric("Approval Rate", f"{country_approval:.1f}%", "+2.3%")
                    with col2:
                        st.metric("Total Volume", f"${country_volume:,.0f}", "+$12.5K")
                    with col3:
                        st.metric("Avg Risk Score", f"{country_avg_risk:.3f}", "-0.05")
                    with col4:
                        st.metric("Transactions", f"{country_txns:,}", "+125")
                    
                    # Channel breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"#### 📱 Channel Distribution - {selected_country}")
                        if 'channel' in country_data.columns:
                            channel_stats = country_data.groupby('channel').size().reset_index(name='count')
                            fig = px.pie(
                                channel_stats,
                                values='count',
                                names='channel',
                                hole=0.4,
                                color_discrete_sequence=px.colors.sequential.Reds_r
                            )
                            fig.update_layout(
                                plot_bgcolor='#0D1117',
                                paper_bgcolor='#161B22',
                                font_color='#C9D1D9',
                                height=350
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"#### 🎯 Solution Mix Performance - {selected_country}")
                        if 'recommended_solution_name' in country_data.columns:
                            solution_stats = country_data.groupby('recommended_solution_name').agg({
                                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100
                            }).reset_index()
                            solution_stats.columns = ['solution', 'approval_rate']
                            solution_stats = solution_stats.nlargest(8, 'approval_rate')
                            
                            fig = px.bar(
                                solution_stats,
                                x='approval_rate',
                                y='solution',
                                orientation='h',
                                color='approval_rate',
                                color_continuous_scale='Greens',
                                labels={'approval_rate': 'Approval Rate (%)'}
                            )
                            fig.update_layout(
                                plot_bgcolor='#0D1117',
                                paper_bgcolor='#161B22',
                                font_color='#C9D1D9',
                                height=350,
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Time series for country
                    st.markdown(f"#### 📈 Hourly Trends - {selected_country}")
                    if 'timestamp' in country_data.columns:
                        country_data['timestamp'] = pd.to_datetime(country_data['timestamp'])
                        hourly = country_data.set_index('timestamp').resample('1H').agg({
                            'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                            'transaction_id': 'count'
                        }).reset_index()
                        hourly.columns = ['timestamp', 'approval_rate', 'txn_count']
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=hourly['timestamp'],
                            y=hourly['approval_rate'],
                            mode='lines+markers',
                            name='Approval Rate',
                            line=dict(color='#3FB950', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(63, 185, 80, 0.1)'
                        ))
                        
                        fig.update_layout(
                            plot_bgcolor='#0D1117',
                            paper_bgcolor='#161B22',
                            font_color='#C9D1D9',
                            height=300,
                            xaxis_title="Time",
                            yaxis_title="Approval Rate (%)",
                            showlegend=False
                        )
                        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
                        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                        
                        st.plotly_chart(fig, use_container_width=True)




def show_smart_checkout(checkout_data):
    """Enhanced Smart Checkout page"""
    st.markdown('<h2 class="section-header-premium">🎯 Smart Checkout Analytics</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box-premium">
        <strong>Smart Checkout</strong> dynamically selects the optimal payment solution mix for each transaction 
        to maximize approval rates while managing risk and cost.
    </div>
    """, unsafe_allow_html=True)
    
    if checkout_data.empty:
        st.warning("No checkout data available")
        return
    
    # Solution mix performance
    if 'recommended_solution_name' in checkout_data.columns:
        solution_stats = checkout_data.groupby('recommended_solution_name').agg({
            'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
            'transaction_id': 'count',
            'risk_score': 'mean'
        }).reset_index()
        solution_stats.columns = ['solution', 'approval_rate', 'txn_count', 'avg_risk']
        solution_stats = solution_stats.sort_values('approval_rate', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Solution Mix Performance")
            fig = px.bar(
                solution_stats,
                x='approval_rate',
                y='solution',
                orientation='h',
                color='approval_rate',
                color_continuous_scale='Greens',
                text='approval_rate',
                labels={'approval_rate': 'Approval Rate (%)'}
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Transaction Distribution")
            fig = px.pie(
                solution_stats,
                values='txn_count',
                names='solution',
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("### 📋 Detailed Solution Performance")
        st.dataframe(
            solution_stats.style.background_gradient(subset=['approval_rate'], cmap='Greens'),
            use_container_width=True,
            height=400
        )

def show_decline_analysis(decline_data, checkout_data):
    """Enhanced decline analysis page"""
    st.markdown('<h2 class="section-header-premium">📉 Decline Analysis & Insights</h2>', unsafe_allow_html=True)
    
    if decline_data.empty:
        st.warning("No decline data available")
        return
    
    # Top decline reasons
    if 'reason_code' in decline_data.columns:
        top_declines = decline_data.groupby('reason_code')['decline_count'].sum().sort_values(ascending=False).head(10)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔴 Top Decline Reasons")
            fig = px.bar(
                x=top_declines.values,
                y=top_declines.index,
                orientation='h',
                color=top_declines.values,
                color_continuous_scale='Reds',
                labels={'x': 'Decline Count', 'y': 'Reason Code'}
            )
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Recommended Actions")
            st.markdown("""
            <div class="danger-box-premium">
                <h4>High Priority</h4>
                <ul>
                    <li>Enable stricter fraud checks for high-risk MCCs</li>
                    <li>Review issuer rules for cross-border</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="warning-box-premium">
                <h4>Medium Priority</h4>
                <ul>
                    <li>Optimize 3DS flow for EU</li>
                    <li>Add network tokenization</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def show_smart_retry(retry_data):
    """Enhanced smart retry page"""
    st.markdown('<h2 class="section-header-premium">🔄 Smart Retry Recommendations</h2>', unsafe_allow_html=True)
    
    if retry_data.empty:
        st.warning("No retry data available")
        return
    
    # Retry recommendation distribution
    if 'retry_recommendation' in retry_data.columns:
        retry_dist = retry_data['retry_recommendation'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            retry_now = retry_dist.get('RETRY_NOW', 0)
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-icon">🔄</div>
                <div class="kpi-label-premium">Retry Now</div>
                <div class="kpi-value-premium">{retry_now}</div>
                <div class="kpi-delta-positive">High success probability</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            retry_later = retry_dist.get('RETRY_LATER', 0)
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-icon">⏰</div>
                <div class="kpi-label-premium">Retry Later</div>
                <div class="kpi-value-premium">{retry_later}</div>
                <div class="kpi-delta-neutral">Wait for optimal timing</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            do_not_retry = retry_dist.get('DO_NOT_RETRY', 0)
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-icon">⛔</div>
                <div class="kpi-label-premium">Do Not Retry</div>
                <div class="kpi-value-premium">{do_not_retry}</div>
                <div class="kpi-delta-negative">Low success probability</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Revenue recovery potential
        if 'expected_recovery_amount' in retry_data.columns:
            total_recovery = retry_data[retry_data['retry_recommendation'] != 'DO_NOT_RETRY']['expected_recovery_amount'].sum()
            
            st.markdown(f"""
            <div class="success-box-premium">
                <h3>💰 Revenue Recovery Potential</h3>
                <p style="font-size: 2rem; font-weight: 700; color: #3FB950; margin: 1rem 0;">
                    ${total_recovery:,.2f}
                </p>
                <p>Estimated recoverable revenue from smart retry recommendations</p>
            </div>
            """, unsafe_allow_html=True)

def show_performance_metrics(checkout_data, decline_data, retry_data):
    """Performance metrics dashboard"""
    st.markdown('<h2 class="section-header-premium">📊 Performance Metrics & Analytics</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🔀 Comparisons", "📉 Detailed Metrics"])
    
    with tab1:
        st.markdown("### Time-Series Performance")
        # Add time series charts
        if not checkout_data.empty and 'timestamp' in checkout_data.columns:
            checkout_data['timestamp'] = pd.to_datetime(checkout_data['timestamp'])
            daily = checkout_data.set_index('timestamp').resample('1D').agg({
                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                'transaction_id': 'count'
            }).reset_index()
            daily.columns = ['date', 'approval_rate', 'txn_count']
            
            fig = px.line(daily, x='date', y='approval_rate', markers=True)
            fig.update_layout(
                plot_bgcolor='#0D1117',
                paper_bgcolor='#161B22',
                font_color='#C9D1D9',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Baseline vs. Optimized")
        # Comparison metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Baseline Approval", "85.0%")
            st.metric("Baseline Volume", "$8.2M")
        with col2:
            st.metric("Optimized Approval", "92.3%", "+7.3%")
            st.metric("Optimized Volume", "$9.5M", "+$1.3M")
    
    with tab3:
        st.markdown("### Detailed Performance Breakdown")
        if not checkout_data.empty:
            st.dataframe(checkout_data.head(100), use_container_width=True, height=400)

def show_genie_assistant():
    """Genie AI assistant page"""
    st.markdown('<h2 class="section-header-premium">🤖 Genie AI Assistant</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box-premium">
        <p>Ask questions in natural language to analyze payment data. Genie AI will query the data and provide insights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example prompts
    st.markdown("### 💡 Example Queries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 What's the approval rate trend for USA?", use_container_width=True):
            st.info("Querying data... The USA approval rate has increased from 84% to 91% over the last 7 days.")
        
        if st.button("🔴 Which issuer has the highest decline rate?", use_container_width=True):
            st.info("Querying data... Issuer_5 has the highest decline rate at 22%, primarily due to security violations.")
        
        if st.button("💰 What's the revenue impact of Smart Checkout?", use_container_width=True):
            st.info("Querying data... Smart Checkout has generated an additional $1.3M in approved volume (+15.8%).")
    
    with col2:
        if st.button("🌍 Compare approval rates: EU vs LATAM", use_container_width=True):
            st.info("Querying data... EU: 93.5% approval, LATAM: 86.2% approval. EU leads by 7.3 percentage points.")
        
        if st.button("🔄 How many transactions are eligible for retry?", use_container_width=True):
            st.info("Querying data... 450 transactions are marked RETRY_NOW with >70% success probability.")
        
        if st.button("🎯 Best performing solution mix today?", use_container_width=True):
            st.info("Querying data... '3DS+NetworkToken' leads with 95.2% approval rate across 1,250 transactions.")
    
    # Custom query
    st.markdown("### ✍️ Ask Your Own Question")
    user_query = st.text_area("Enter your question:", placeholder="e.g., What are the top 3 decline reasons in Germany?", height=100)
    
    if st.button("🔍 Ask Genie", type="primary", use_container_width=True):
        if user_query:
            with st.spinner("Genie is analyzing..."):
                st.success(f"Query received: '{user_query}' - Genie would process this against Unity Catalog tables.")

def show_settings():
    """Settings and configuration page"""
    st.markdown('<h2 class="section-header-premium">⚙️ Settings & Configuration</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 App Settings", "🗄️ Data Configuration", "👤 User Preferences"])
    
    with tab1:
        st.markdown("### Application Settings")
        
        refresh_interval = st.slider("Auto-refresh interval (seconds)", 10, 300, 60, 10)
        st.checkbox("Enable real-time updates", value=True)
        st.checkbox("Show advanced metrics", value=False)
        st.selectbox("Default view", ["Executive Dashboard", "Geo-Analytics", "Smart Checkout"])
    
    with tab2:
        st.markdown("### Data Source Configuration")
        
        catalog = st.text_input("Unity Catalog", value="payments_lakehouse")
        schema_silver = st.text_input("Silver Schema", value="silver")
        schema_gold = st.text_input("Gold Schema", value="gold")
        
        if st.button("Test Connection"):
            st.success("✅ Successfully connected to Unity Catalog")
    
    with tab3:
        st.markdown("### User Preferences")
        
        theme = st.selectbox("Theme", ["Dark (Default)", "Light", "Auto"])
        language = st.selectbox("Language", ["English", "Spanish", "Portuguese", "German"])
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "CET", "JST"])




if __name__ == "__main__":
    main()


#   /Workspace/Users/<your-email>/payment-authorization-premium --overwrite
#   --source-code-path /Workspace/Users/<your-email>/payment-authorization-premium
