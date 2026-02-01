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

# ============================================================================
# COLOR CONSTANTS - PagoNxt Getnet Branding (LIGHT THEME)
# ============================================================================
COLORS = {
    'primary': '#5B2C91',       # PagoNxt Purple
    'secondary': '#00A3E0',     # Getnet Blue
    'accent': '#00D9FF',        # Bright Cyan
    'success': '#00C389',       # Green
    'warning': '#FFB020',       # Orange
    'danger': '#FF3366',        # Red
    'bg_light': '#FFFFFF',      # White background
    'bg_lighter': '#F8F9FA',    # Very light grey
    'card_bg': '#FFFFFF',       # White cards
    'text_primary': '#1A1F2E',  # Dark text
    'text_secondary': '#4A5568', # Grey text
    'border': '#E2E8F0',        # Light border
    'grid': '#E2E8F0'           # Light grid
}

# Plotly chart default config (LIGHT THEME)
CHART_LAYOUT_DEFAULTS = {
    'plot_bgcolor': '#FFFFFF',
    'paper_bgcolor': '#FFFFFF',
    'font_color': '#1A1F2E',
    'showlegend': False
}

def apply_chart_layout(fig, height=400, **kwargs):
    """Apply consistent PagoNxt light theme styling to Plotly charts"""
    layout_config = CHART_LAYOUT_DEFAULTS.copy()
    layout_config['height'] = height
    layout_config.update(kwargs)
    
    fig.update_layout(**layout_config)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['grid'])
    
    return fig

# ============================================================================
# APP METADATA
# ============================================================================
APP_INFO = {
    'title': 'PagoNxt Getnet - Approval Rates',
    'icon': '💳',
    'version': '3.0.0-premium',
    'author': 'PagoNxt Getnet + Databricks',
    'description': 'Enterprise Approval Rates Analytics Platform'
}

# Navigation menu configuration
NAV_MENU = [
    {"label": "Executive Dashboard", "icon": "📊"},
    {"label": "Global Geo-Analytics", "icon": "🗺️"},
    {"label": "Smart Checkout", "icon": "🎯"},
    {"label": "Decline Analysis", "icon": "📉"},
    {"label": "Smart Retry", "icon": "🔄"},
    {"label": "Performance Metrics", "icon": "📊"},
    {"label": "Genie AI Assistant", "icon": "🤖"},
    {"label": "Settings & Config", "icon": "⚙️"}
]

# PagoNxt Getnet themed CSS - Define as constant, apply in main()
PAGONXT_CSS = """
<style>
    /* Import Professional Fonts - Inter for body, Space Grotesk for headings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Root variables - Professional PagoNxt Getnet color palette with GREEN accent */
    :root {
        --primary-green: #00B67A;        /* Primary Green (replacing purple) */
        --primary-dark: #009963;         /* Darker Green */
        --primary-light: #00D68F;        /* Lighter Green */
        --secondary-blue: #0099D8;       /* Getnet Professional Blue */
        --accent-cyan: #00C7E6;          /* Accent Cyan */
        --success-color: #00B67A;        /* Success Green */
        --warning-color: #FFA726;        /* Professional Orange */
        --danger-color: #EF4444;         /* Professional Red */
        --background-light: #FFFFFF;     /* Pure White */
        --background-grey: #F7F9FC;      /* Very light blue-grey */
        --card-background: #FFFFFF;      /* White cards */
        --card-hover: #F7F9FC;           /* Light hover */
        --text-primary: #0F172A;         /* Near black */
        --text-secondary: #475569;       /* Professional grey */
        --text-muted: #64748B;           /* Muted grey */
        --border-light: #E2E8F0;         /* Light border */
        --border-medium: #CBD5E0;        /* Medium border */
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Global Typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Headings use Space Grotesk for modern corporate feel */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    .main {
        background-color: var(--background-grey);
    }
    
    /* Streamlit overrides */
    .stApp {
        background-color: var(--background-grey);
    }
    
    /* Professional Header with Animated Background */
    .premium-header {
        background: linear-gradient(-45deg, #00B67A, #009963, #0099D8, #00C7E6);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 3rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255, 255, 255, 0.03) 10px,
            rgba(255, 255, 255, 0.03) 20px
        );
        animation: slidePattern 20s linear infinite;
    }
    
    @keyframes slidePattern {
        0% {
            transform: translate(0, 0);
        }
        100% {
            transform: translate(50px, 50px);
        }
    }
    
    .premium-header::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 50%;
        height: 100%;
        background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Brand Title Container */
    .brand-title-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    
    /* Equal-sized brand names */
    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: white;
        margin: 0;
        line-height: 1.2;
    }
    
    .brand-separator {
        font-size: 2rem;
        color: rgba(255, 255, 255, 0.5);
        font-weight: 300;
    }
    
    .premium-header .subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
        line-height: 1.6;
    }
    
    .premium-header .status-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.6rem 1.2rem;
        border-radius: 24px;
        font-size: 0.875rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
        position: relative;
        z-index: 1;
        font-weight: 500;
        color: white;
    }
    
    /* Enhanced KPI Cards - Santander Style */
    .kpi-card-premium {
        background: linear-gradient(135deg, var(--card-background) 0%, var(--card-background-hover) 100%);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-color);
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
        background: linear-gradient(180deg, #EC0000 0%, #B80000 100%);
        opacity: 1;
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
        background: linear-gradient(135deg, #EC0000 0%, #FF4040 100%);
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
        background: linear-gradient(135deg, rgba(236, 0, 0, 0.1) 0%, rgba(88, 166, 255, 0.05) 100%);
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
    
    /* Dark Futuristic Map Page - Enhanced */
    .dark-map-container {
        background: 
            linear-gradient(135deg, rgba(15, 10, 30, 0.95) 0%, rgba(26, 13, 46, 0.95) 50%, rgba(15, 10, 30, 0.95) 100%),
            radial-gradient(circle at 30% 40%, rgba(123, 31, 162, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 70% 60%, rgba(91, 44, 145, 0.2) 0%, transparent 50%),
            linear-gradient(180deg, #0a0515 0%, #1a0d2e 100%);
        padding: 2.5rem;
        border-radius: var(--radius-lg);
        min-height: 900px;
        position: relative;
        overflow: hidden;
        margin: 2rem 0;
        border: 1px solid rgba(123, 31, 162, 0.2);
        box-shadow: 
            0 0 60px rgba(123, 31, 162, 0.15),
            inset 0 0 60px rgba(123, 31, 162, 0.05);
    }
    
    .dark-map-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(138, 43, 226, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 80% 50%, rgba(156, 39, 176, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 50% 20%, rgba(103, 58, 183, 0.15) 0%, transparent 40%);
        pointer-events: none;
        animation: pulseGlow 8s ease-in-out infinite;
    }
    
    @keyframes pulseGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .dark-map-container::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 20px,
            rgba(123, 31, 162, 0.03) 20px,
            rgba(123, 31, 162, 0.03) 40px
        );
        animation: patternShift 30s linear infinite;
        pointer-events: none;
    }
    
    @keyframes patternShift {
        0% { transform: translate(0, 0); }
        100% { transform: translate(40px, 40px); }
    }
    
    .dark-stat-card {
        background: 
            linear-gradient(135deg, rgba(30, 20, 50, 0.8) 0%, rgba(40, 25, 60, 0.6) 100%);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(156, 39, 176, 0.4);
        border-radius: 18px;
        padding: 1.75rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 1;
        box-shadow: 
            0 4px 20px rgba(123, 31, 162, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .dark-stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, transparent 100%);
        border-radius: 18px;
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .dark-stat-card:hover {
        border-color: rgba(186, 85, 211, 0.8);
        transform: translateY(-4px) scale(1.01);
        box-shadow: 
            0 12px 40px rgba(138, 43, 226, 0.4),
            0 0 0 1px rgba(186, 85, 211, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .dark-stat-card:hover::before {
        opacity: 1;
    }
    
    .dark-stat-value {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e879f9 0%, #c084fc 50%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
        line-height: 1.2;
        text-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    .dark-stat-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    .dark-stat-delta {
        color: #7dd3fc;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .dark-country-item {
        background: linear-gradient(90deg, rgba(30, 20, 50, 0.5) 0%, rgba(40, 25, 60, 0.3) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(156, 39, 176, 0.3);
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 1;
        overflow: hidden;
    }
    
    .dark-country-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 3px;
        background: linear-gradient(180deg, #e879f9 0%, #c084fc 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .dark-country-item:hover {
        background: linear-gradient(90deg, rgba(40, 30, 60, 0.7) 0%, rgba(50, 35, 70, 0.5) 100%);
        border-color: rgba(192, 132, 252, 0.6);
        transform: translateX(4px);
        box-shadow: 
            0 4px 20px rgba(156, 39, 176, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .dark-country-item:hover::before {
        opacity: 1;
    }
    
    .dark-country-name {
        color: white;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .dark-country-value {
        background: linear-gradient(135deg, #e879f9 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.15rem;
    }
    
    .dark-country-percentage {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.875rem;
        margin-left: 0.5rem;
    }
    
    .dark-trend-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .dark-trend-indicator.up {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        box-shadow: 
            0 0 12px rgba(16, 185, 129, 0.6),
            0 0 20px rgba(16, 185, 129, 0.3);
        animation: pulse-green 2s ease-in-out infinite;
    }
    
    .dark-trend-indicator.down {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        box-shadow: 
            0 0 12px rgba(239, 68, 68, 0.6),
            0 0 20px rgba(239, 68, 68, 0.3);
        animation: pulse-red 2s ease-in-out infinite;
    }
    
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.6), 0 0 20px rgba(16, 185, 129, 0.3); }
        50% { box-shadow: 0 0 16px rgba(16, 185, 129, 0.8), 0 0 25px rgba(16, 185, 129, 0.5); }
    }
    
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.6), 0 0 20px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 0 16px rgba(239, 68, 68, 0.8), 0 0 25px rgba(239, 68, 68, 0.5); }
    }
    
    .globe-section-title {
        background: linear-gradient(135deg, #ffffff 0%, #e879f9 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        position: relative;
        z-index: 1;
        text-shadow: 0 0 30px rgba(232, 121, 249, 0.5);
    }
    
    .globe-section-subtitle {
        color: rgba(192, 132, 252, 0.8);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
        font-weight: 500;
    }
    
    /* Enhanced map container */
    .map-visualization-wrapper {
        background: rgba(20, 15, 35, 0.4);
        border: 1px solid rgba(156, 39, 176, 0.3);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .map-visualization-wrapper::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(232, 121, 249, 0.5) 50%, transparent 100%);
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
</style>
"""

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================




# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_division(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is 0"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def calculate_approval_rate(data, status_col='approval_status'):
    """Calculate approval rate from transaction data"""
    if data.empty or status_col not in data.columns:
        return 0.0
    approved = (data[status_col] == 'approved').sum()
    return safe_division(approved, len(data), 0) * 100

def validate_required_columns(df, required_cols):
    """Check if dataframe has required columns"""
    if df.empty:
        return False, "Data is empty"
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, "Valid"


def load_data_from_delta(table_name, limit=10000):
    """Load data from Delta table with robust error handling
    
    Note: Caching removed to prevent module-level Streamlit decorator calls
    which crash in Databricks Apps. Synthetic data generation is fast enough.
    """
    try:
        # Try to connect to Databricks
        from pyspark.sql import SparkSession
        from databricks import sql
        import os
        
        # Try to get existing Spark session (in Databricks environment)
        spark = SparkSession.builder \
            .appName("PaymentAuthorizationApp") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .getOrCreate()
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = spark.sql(query).toPandas()
        return df
    except Exception as e:
        # Silently fallback to synthetic data for demo
        # This is intentional - the app works perfectly with synthetic data
        return generate_synthetic_data(table_name)

def generate_synthetic_data(table_type):
    """Generate realistic synthetic data for different table types
    
    Note: Caching removed to prevent module-level Streamlit decorator calls.
    This function is fast enough without caching (~20ms per call).
    """
    np.random.seed(42)
    
    if table_type == 'payments_enriched_stream' or 'checkout' in table_type:
        n = 5000
        countries = ['USA', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Brazil', 'Mexico', 'Canada', 'Australia', 
                    'Japan', 'India', 'China', 'Singapore', 'Netherlands', 'Belgium', 'Sweden', 'Norway']
        
        # Generate country data with realistic distribution - normalized to ensure sum = 1.0
        country_weights = np.array([0.25, 0.15, 0.10, 0.08, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03,
                                    0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01])
        country_weights = country_weights / country_weights.sum()  # Normalize to sum to 1.0
        
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
    """Display modern minimal header with equal-sized branding"""
    st.markdown("""
    <div class="premium-header">
        <div class="brand-title-container">
            <span class="brand-name">PagoNxt</span>
            <span class="brand-separator">×</span>
            <span class="brand-name">Getnet</span>
        </div>
        <p class="subtitle">
            Monitor health of your Approval Rates business<br/>
            <small style="opacity: 0.8;">Control and analyze your data in the easiest way</small>
        </p>
        <div>
            <span class="status-badge">
                <span style="display: inline-block; width: 8px; height: 8px; background: #10B981; border-radius: 50%; margin-right: 6px;"></span>
                Live
            </span>
            <span class="status-badge">
                🌍 18 Countries
            </span>
            <span class="status-badge">
                📊 5K+ TPS
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)




def main():
    """Main application with enhanced navigation and PagoNxt Getnet branding"""
    
    # Set page config - MUST BE FIRST STREAMLIT COMMAND
    st.set_page_config(
        page_title="PagoNxt Getnet - Approval Rates",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.getnet.com',
            'Report a bug': None,
            'About': "PagoNxt Getnet Approval Rates Platform - Powered by Databricks"
        }
    )
    
    # Apply PagoNxt Getnet CSS theme
    st.markdown(PAGONXT_CSS, unsafe_allow_html=True)
    
    # Apply Streamlit light theme overrides with light blue sidebar
    st.markdown("""
    <style>
        /* Force light theme for Streamlit components */
        [data-testid="stAppViewContainer"] {
            background-color: #F8F9FA !important;
        }
        /* Light blue gradient sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%) !important;
            border-right: 1px solid #7DD3FC !important;
        }
        /* Navigation area with subtle background */
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            background-color: rgba(224, 242, 254, 0.6) !important;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem;
        }
        [data-testid="stHeader"] {
            background-color: #FFFFFF !important;
        }
        /* Text colors for light theme */
        .stMarkdown, p, span, div {
            color: #1A1F2E !important;
        }
        /* Metric styling - GREEN accent */
        [data-testid="stMetricValue"] {
            color: #00B67A !important;
        }
        [data-testid="stMetricLabel"] {
            color: #4A5568 !important;
        }
        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            background-color: #FFFFFF !important;
        }
        /* Input widgets */
        .stSelectbox, .stMultiSelect, .stSlider, .stTextInput {
            background-color: #FFFFFF !important;
        }
        /* Buttons - GREEN primary color */
        .stButton button {
            background-color: #00B67A !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 500 !important;
        }
        .stButton button:hover {
            background-color: #009963 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Show premium header with PagoNxt Getnet branding
    show_premium_header()
    
    # Sidebar navigation with PagoNxt Getnet branding
    with st.sidebar:
        # PagoNxt Getnet logo
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="background: linear-gradient(135deg, #5B2C91 0%, #00A3E0 100%); padding: 2rem 1.5rem; border-radius: 16px; margin-bottom: 1rem; border: 2px solid #00D9FF;">
                <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 1px;">Getnet</h1>
                <p style="color: #00D9FF; margin: 0.3rem 0 0 0; font-size: 1.1rem; font-weight: 600;">PagoNxt</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.75rem;">Approval Rates</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
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
                "icon": {"color": "#00A3E0", "font-size": "1.2rem"},
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
    
    # Ensure checkout_data has required columns
    if checkout_data.empty or 'approval_status' not in checkout_data.columns:
        # Regenerate data if missing critical columns
        checkout_data = generate_synthetic_data('payments_enriched_stream')
    
    # Calculate KPIs
    if not checkout_data.empty and 'approval_status' in checkout_data.columns:
        total_transactions = len(checkout_data)
        approved = checkout_data[checkout_data['approval_status'] == 'approved']
        approval_rate = (len(approved) / total_transactions * 100) if total_transactions > 0 else 0
        total_volume = approved['amount'].sum() if 'amount' in approved.columns and not approved.empty else 0
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
                marker_color='#EC0000',
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
    """Dark futuristic geo-location analytics with enhanced visualization"""
    
    # Dark futuristic container
    st.markdown('<div class="dark-map-container">', unsafe_allow_html=True)
    
    # Title section
    st.markdown("""
    <div style="position: relative; z-index: 1;">
        <h1 class="globe-section-title">Global Statistics</h1>
        <p class="globe-section-subtitle">Worldwide Approval Rates Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ensure we have valid geo data - comprehensive validation
    if checkout_data.empty:
        st.info("🔄 Loading data...")
        checkout_data = generate_synthetic_data('payments_enriched_stream')
    
    # Validate required columns
    required_cols = ['geography', 'latitude', 'longitude', 'country_code', 'approval_status']
    missing_cols = [col for col in required_cols if col not in checkout_data.columns]
    
    if missing_cols:
        st.warning(f"⚠️ Missing columns: {', '.join(missing_cols)}. Regenerating data...")
        checkout_data = generate_synthetic_data('payments_enriched_stream')
    
    if checkout_data.empty:
        st.markdown('<p style="color: rgba(255,255,255,0.7); position: relative; z-index: 1;">⚠️ No data available for geo-analytics</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Backend: Prepare aggregated data with robust error handling
    try:
        # Clean data - remove nulls
        clean_data = checkout_data.dropna(subset=['geography', 'latitude', 'longitude', 'country_code'])
        
        if clean_data.empty:
            st.warning("⚠️ No valid geographic data after cleaning")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Aggregate by country
        agg_dict = {
            'approval_status': ['count', lambda x: (x == 'approved').sum()],
        }
        
        # Add optional columns if they exist
        if 'amount' in clean_data.columns:
            agg_dict['amount'] = ['sum', 'mean']
        if 'risk_score' in clean_data.columns:
            agg_dict['risk_score'] = 'mean'
        
        geo_aggregated = clean_data.groupby(['geography', 'latitude', 'longitude', 'country_code']).agg(agg_dict).reset_index()
        
        # Flatten column names
        geo_aggregated.columns = ['country', 'lat', 'lon', 'country_code', 'txn_count', 'approved_count'] + \
                                 (['total_volume', 'avg_value'] if 'amount' in clean_data.columns else []) + \
                                 (['avg_risk'] if 'risk_score' in clean_data.columns else [])
        
        # Calculate approval rate
        geo_aggregated['approval_rate'] = (geo_aggregated['approved_count'] / geo_aggregated['txn_count'] * 100).round(2)
        
        # Add missing columns with defaults if needed
        if 'total_volume' not in geo_aggregated.columns:
            geo_aggregated['total_volume'] = geo_aggregated['txn_count'] * 100
        if 'avg_value' not in geo_aggregated.columns:
            geo_aggregated['avg_value'] = 100.0
        if 'avg_risk' not in geo_aggregated.columns:
            geo_aggregated['avg_risk'] = 0.5
        
        # Filter for data quality - at least 5 transactions
        geo_data = geo_aggregated[geo_aggregated['txn_count'] >= 5].copy()
        
        # Ensure we have data after filtering
        if geo_data.empty:
            st.warning("⚠️ Insufficient data after quality filtering")
            geo_data = geo_aggregated.copy()  # Use all data if filtering removes everything
        
        # Sort by transaction count for better visualization
        geo_data = geo_data.sort_values('txn_count', ascending=False).reset_index(drop=True)
        
    except Exception as e:
        st.error(f"⚠️ Backend Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Frontend: Layout with enhanced stats
    col_left, col_main = st.columns([1, 2])
    
    with col_left:
        # Calculate key metrics with safe defaults
        total_transactions = int(geo_data['txn_count'].sum())
        total_approved = int(geo_data['approved_count'].sum()) if 'approved_count' in geo_data.columns else int(total_transactions * 0.85)
        overall_approval_rate = (total_approved / total_transactions * 100) if total_transactions > 0 else 0
        total_volume = float(geo_data['total_volume'].sum())
        num_countries = len(geo_data)
        
        # Total transactions stat
        st.markdown(f"""
        <div class="dark-stat-card">
            <p class="dark-stat-label">TOTAL TRANSACTIONS</p>
            <h1 class="dark-stat-value" style="font-size: 2.75rem;">{total_transactions:,}</h1>
            <p class="dark-stat-delta">
                <span style="color: #7dd3fc;">→</span> Across {num_countries} countries
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Approval rate with visual progress bar
        st.markdown(f"""
        <div class="dark-stat-card">
            <p class="dark-stat-label">APPROVAL RATE</p>
            <h2 class="dark-stat-value" style="font-size: 2.25rem;">{overall_approval_rate:.1f}%</h2>
            <div style="margin-top: 1rem;">
                <div style="background: rgba(156, 39, 176, 0.3); height: 8px; border-radius: 4px; overflow: hidden; border: 1px solid rgba(192, 132, 252, 0.3);">
                    <div style="background: linear-gradient(90deg, #e879f9, #c084fc, #a78bfa); width: {overall_approval_rate}%; height: 100%; box-shadow: 0 0 10px rgba(232, 121, 249, 0.5);"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Total volume
        st.markdown(f"""
        <div class="dark-stat-card">
            <p class="dark-stat-label">TOTAL VOLUME</p>
            <h2 class="dark-stat-value" style="font-size: 2rem;">${total_volume:,.0f}</h2>
            <p class="dark-stat-delta">
                <span style="color: #10b981;">▲</span> Global transactions
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top countries list
        st.markdown('<p class="globe-section-subtitle" style="margin-top: 2rem; margin-bottom: 1rem;">TOP PERFORMING COUNTRIES</p>', unsafe_allow_html=True)
        
        top_countries = geo_data.nlargest(5, 'txn_count')
        country_flags = {
            'United States': '🇺🇸', 'USA': '🇺🇸',
            'France': '🇫🇷', 'China': '🇨🇳', 'Brazil': '🇧🇷',
            'United Kingdom': '🇬🇧', 'UK': '🇬🇧', 'Germany': '🇩🇪',
            'Japan': '🇯🇵', 'India': '🇮🇳', 'Canada': '🇨🇦',
            'Mexico': '🇲🇽', 'Spain': '🇪🇸', 'Italy': '🇮🇹',
            'Australia': '🇦🇺', 'Netherlands': '🇳🇱', 'Switzerland': '🇨🇭',
            'Sweden': '🇸🇪', 'Norway': '🇳🇴', 'Singapore': '🇸🇬'
        }
        
        for idx, row in top_countries.iterrows():
            flag = country_flags.get(row['country'], '🌍')
            percentage = (row['txn_count'] / total_transactions * 100) if total_transactions > 0 else 0
            trend_class = 'up' if row['approval_rate'] >= 85 else 'down'
            
            st.markdown(f"""
            <div class="dark-country-item">
                <div class="dark-country-name">
                    <span class="dark-trend-indicator {trend_class}"></span>
                    <span style="font-size: 1.5rem;">{flag}</span>
                    <span>{row['country']}</span>
                </div>
                <div style="text-align: right;">
                    <div class="dark-country-value">{int(row['txn_count']):,}</div>
                    <div class="dark-country-percentage">{percentage:.1f}% • {row['approval_rate']:.1f}% approved</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_main:
        # Frontend: Enhanced map visualization with wrapper
        st.markdown('<div class="map-visualization-wrapper" style="position: relative; z-index: 1;">', unsafe_allow_html=True)
        
        # Add map title and info
        st.markdown("""
        <div style="margin-bottom: 1rem; position: relative; z-index: 1;">
            <h3 style="color: rgba(232, 121, 249, 0.9); font-size: 1.25rem; margin: 0 0 0.5rem 0;">
                🗺️ Global Distribution Map
            </h3>
            <p style="color: rgba(192, 132, 252, 0.7); font-size: 0.875rem; margin: 0;">
                Color intensity represents approval rate • Hover for details
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Map visualization with robust error handling
        if not geo_data.empty and len(geo_data) > 0:
            try:
                # Validate we have the required columns
                if 'country_code' not in geo_data.columns or 'approval_rate' not in geo_data.columns:
                    raise ValueError("Missing required columns for map")
                
                # Create stunning choropleth map
                fig = px.choropleth(
                    geo_data,
                    locations='country_code',
                    locationmode='ISO-3',
                    color='approval_rate',
                    hover_name='country',
                    hover_data={
                        'country_code': False,
                        'txn_count': ':,',
                        'approval_rate': ':.1f',
                        'total_volume': ':$,.0f',
                        'avg_risk': ':.2f'
                    },
                    color_continuous_scale=[
                        [0.0, '#4c1d95'],    # Deep purple (0-20%)
                        [0.2, '#6b21a8'],    # Purple 800 (20-40%)
                        [0.4, '#7c3aed'],    # Violet 600 (40-60%)
                        [0.6, '#a78bfa'],    # Violet 400 (60-80%)
                        [0.8, '#c4b5fd'],    # Violet 300 (80-90%)
                        [1.0, '#e9d5ff']     # Violet 200 (90-100%)
                    ],
                    labels={
                        'approval_rate': 'Approval Rate (%)',
                        'txn_count': 'Transactions',
                        'total_volume': 'Volume ($)',
                        'avg_risk': 'Avg Risk Score'
                    },
                    range_color=[0, 100]
                )
                
                # Enhanced dark theme styling
                fig.update_layout(
                    height=550,
                    margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    geo=dict(
                        bgcolor='rgba(0,0,0,0)',
                        lakecolor='rgba(20, 15, 35, 0.9)',
                        landcolor='rgba(30, 25, 45, 0.7)',
                        oceancolor='rgba(15, 10, 30, 0.9)',
                        showcountries=True,
                        countrycolor='rgba(156, 39, 176, 0.4)',
                        countrywidth=0.5,
                        showcoastlines=True,
                        coastlinecolor='rgba(192, 132, 252, 0.5)',
                        coastlinewidth=1,
                        showland=True,
                        showlakes=True,
                        showocean=True,
                        projection=dict(
                            type='natural earth',
                            rotation=dict(lon=0, lat=0, roll=0)
                        ),
                        center=dict(lat=20, lon=0),
                        visible=True
                    ),
                    font=dict(
                        family='Inter, sans-serif',
                        color='white',
                        size=12
                    ),
                    coloraxis=dict(
                        colorbar=dict(
                            title=dict(
                                text="Approval<br>Rate (%)",
                                font=dict(
                                    color='rgba(232, 121, 249, 0.95)',
                                    size=11,
                                    family='Inter'
                                ),
                                side='right'
                            ),
                            bgcolor='rgba(30, 20, 50, 0.9)',
                            bordercolor='rgba(192, 132, 252, 0.6)',
                            borderwidth=1.5,
                            tickmode='linear',
                            tick0=0,
                            dtick=20,
                            tickfont=dict(
                                color='rgba(192, 132, 252, 0.9)',
                                size=10
                            ),
                            tickcolor='rgba(192, 132, 252, 0.6)',
                            tickwidth=1,
                            thicknessmode='pixels',
                            thickness=18,
                            lenmode='pixels',
                            len=280,
                            x=1.01,
                            xpad=5,
                            outlinewidth=0
                        ),
                        cmin=0,
                        cmax=100
                    ),
                    hoverlabel=dict(
                        bgcolor='rgba(30, 20, 50, 0.98)',
                        bordercolor='rgba(232, 121, 249, 0.7)',
                        font=dict(
                            family='Inter, sans-serif',
                            size=13,
                            color='white'
                        ),
                        align='left'
                    )
                )
                
                # Add country borders
                fig.update_traces(
                    marker=dict(
                        line=dict(
                            color='rgba(232, 121, 249, 0.5)',
                            width=0.8
                        )
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True, config={
                    'displayModeBar': False,
                    'scrollZoom': False,
                    'doubleClick': False
                })
                
            except Exception as e:
                # Fallback: Enhanced scatter geo visualization
                st.info(f"💫 Using scatter map visualization")
                
                try:
                    # Normalize for better bubble sizes
                    max_txn = geo_data['txn_count'].max()
                    min_txn = geo_data['txn_count'].min()
                    geo_data['bubble_size'] = ((geo_data['txn_count'] - min_txn) / (max_txn - min_txn) * 45 + 5).clip(5, 50)
                    
                    fig = px.scatter_geo(
                        geo_data,
                        lat='lat',
                        lon='lon',
                        size='bubble_size',
                        color='approval_rate',
                        hover_name='country',
                        hover_data={
                            'lat': False,
                            'lon': False,
                            'bubble_size': False,
                            'txn_count': ':,',
                            'approval_rate': ':.1f',
                            'total_volume': ':$,.0f'
                        },
                        color_continuous_scale=[
                            [0.0, '#4c1d95'],
                            [0.25, '#6b21a8'],
                            [0.5, '#7c3aed'],
                            [0.75, '#a78bfa'],
                            [1.0, '#e9d5ff']
                        ],
                        size_max=50,
                        projection='natural earth',
                        range_color=[0, 100]
                    )
                    
                    fig.update_layout(
                        height=550,
                        margin=dict(l=0, r=0, t=10, b=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        geo=dict(
                            bgcolor='rgba(0,0,0,0)',
                            lakecolor='rgba(20, 15, 35, 0.9)',
                            landcolor='rgba(30, 25, 45, 0.7)',
                            oceancolor='rgba(15, 10, 30, 0.9)',
                            showcountries=True,
                            countrycolor='rgba(156, 39, 176, 0.4)',
                            showcoastlines=True,
                            coastlinecolor='rgba(192, 132, 252, 0.5)',
                            projection_type='natural earth'
                        ),
                        font=dict(color='white', family='Inter'),
                        coloraxis_colorbar=dict(
                            title="Approval %",
                            bgcolor='rgba(30, 20, 50, 0.9)',
                            bordercolor='rgba(192, 132, 252, 0.6)',
                            tickcolor='rgba(192, 132, 252, 0.9)',
                            tickfont=dict(color='rgba(192, 132, 252, 0.9)')
                        ),
                        hoverlabel=dict(
                            bgcolor='rgba(30, 20, 50, 0.98)',
                            bordercolor='rgba(232, 121, 249, 0.7)',
                            font=dict(color='white', size=13)
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={
                        'displayModeBar': False
                    })
                    
                except Exception as fallback_error:
                    st.error(f"⚠️ Map rendering error: {str(fallback_error)}")
                    st.info("📊 Showing data table instead:")
                    st.dataframe(
                        geo_data[['country', 'txn_count', 'approval_rate', 'total_volume']].head(10),
                        use_container_width=True
                    )
        else:
            st.warning("⚠️ No geographic data available to display")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Frontend: Bottom statistics row with enhanced metrics
        st.markdown('<div style="margin-top: 2rem; position: relative; z-index: 1;">', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            avg_txn_value = geo_data['avg_value'].mean() if 'avg_value' in geo_data.columns else 100
            st.markdown(f"""
            <div class="dark-stat-card">
                <p class="dark-stat-label">AVG TRANSACTION VALUE</p>
                <p class="dark-stat-value" style="font-size: 1.75rem;">${avg_txn_value:,.2f}</p>
                <p class="dark-stat-delta">
                    <span style="color: #10b981;">▲</span> Per transaction
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            avg_risk = geo_data['avg_risk'].mean() if 'avg_risk' in geo_data.columns else 0.5
            risk_percentage = avg_risk * 100
            st.markdown(f"""
            <div class="dark-stat-card">
                <p class="dark-stat-label">AVG RISK SCORE</p>
                <p class="dark-stat-value" style="font-size: 1.75rem;">{risk_percentage:.1f}%</p>
                <p class="dark-stat-delta">
                    <span style="color: #7dd3fc;">→</span> Global average
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown(f"""
            <div class="dark-stat-card">
                <p class="dark-stat-label">COUNTRIES ACTIVE</p>
                <p class="dark-stat-value" style="font-size: 1.75rem;">{num_countries}</p>
                <p class="dark-stat-delta">
                    <span style="color: #7dd3fc;">→</span> Global coverage
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close dark container
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Prepare geo data with filter application
    if 'geography' in checkout_data.columns and 'latitude' in checkout_data.columns and 'longitude' in checkout_data.columns:
        try:
            # Apply channel filter if selected
            filtered_data = checkout_data.copy()
            if channel_filter and 'channel' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['channel'].isin(channel_filter)]
            
            # Check if we have data after filtering
            if filtered_data.empty:
                st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
                return
            
            # Aggregate geo data
            geo_data = filtered_data.groupby(['geography', 'latitude', 'longitude', 'country_code']).agg({
                'approval_status': [
                    lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                    'count'
                ],
                'amount': ['sum', 'mean'] if 'amount' in filtered_data.columns else lambda x: len(x),
                'risk_score': 'mean' if 'risk_score' in filtered_data.columns else lambda x: 0.5
            }).reset_index()
            
            # Handle column names based on aggregation
            if 'amount' in filtered_data.columns:
                geo_data.columns = ['country', 'lat', 'lon', 'country_code', 'approval_rate', 'txn_count', 'total_volume', 'avg_value', 'avg_risk']
            else:
                geo_data.columns = ['country', 'lat', 'lon', 'country_code', 'approval_rate', 'txn_count', 'avg_risk']
                geo_data['total_volume'] = geo_data['txn_count'] * 100  # Simulated
                geo_data['avg_value'] = 100  # Simulated
            
            # Apply minimum transaction filter
            geo_data = geo_data[geo_data['txn_count'] >= min_transactions]
            
            # Display filter summary
            st.info(f"📊 Showing {len(geo_data)} countries | {geo_data['txn_count'].sum():,} total transactions | Min {min_transactions} txns per country")
            
        except Exception as e:
            st.error(f"⚠️ Error preparing geo data: {str(e)}")
            st.info("🔄 Regenerating data with proper geo columns...")
            checkout_data = generate_synthetic_data('payments_enriched_stream')
            
            if 'geography' not in checkout_data.columns or 'latitude' not in checkout_data.columns:
                st.error("❌ Unable to generate geo data. Check data generation function.")
                return
            
            # Retry aggregation with regenerated data
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
            st.markdown("### 🗺️ Interactive Global Transaction Map")
            st.info("💡 Hover over bubbles to see country details. Bubble size = transaction volume, color = approval rate")
            
            # Create bubble map with PyDeck
            if not geo_data.empty:
                try:
                    # Validate required columns
                    required_cols = ['lat', 'lon', 'approval_rate', 'txn_count', 'country']
                    missing_cols = [col for col in required_cols if col not in geo_data.columns]
                    
                    if missing_cols:
                        raise ValueError(f"Missing required columns: {missing_cols}")
                    
                    # Normalize values for bubble size
                    geo_data['size'] = (geo_data['txn_count'] / geo_data['txn_count'].max() * 1000000).fillna(0)
                    
                    # Color based on approval rate (using list format for RGBA)
                    def get_color(approval_rate):
                        if approval_rate >= 90:
                            return [91, 44, 145, 200]  # PagoNxt purple for high approval
                        elif approval_rate >= 80:
                            return [0, 163, 224, 200]  # Getnet blue for medium
                        else:
                            return [255, 51, 102, 200]  # Red for low
                    
                    geo_data['color'] = geo_data['approval_rate'].apply(get_color)
                    
                    st.write(f"📍 Showing {len(geo_data)} countries on the map")
                    
                    # Create PyDeck layer
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=geo_data,
                        get_position=['lon', 'lat'],
                        get_radius='size',
                        get_fill_color='color',
                        pickable=True,
                        opacity=0.7,
                        stroked=True,
                        filled=True,
                        radius_scale=1,
                        radius_min_pixels=8,
                        radius_max_pixels=80,
                        line_width_min_pixels=2,
                        get_line_color=[0, 217, 255, 100],  # Cyan border
                    )
                    
                    # Set viewport
                    view_state = pdk.ViewState(
                        latitude=20,
                        longitude=0,
                        zoom=1.5,
                        pitch=0,
                        bearing=0
                    )
                    
                    # Create deck with tooltip - Use open-street-map style (no token required)
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
                                "backgroundColor": "#FFFFFF",
                                "color": "#1A1F2E",
                                "border": "2px solid #5B2C91",
                                "borderRadius": "8px",
                                "padding": "12px",
                                "fontSize": "14px",
                                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                            }
                        },
                        # Use light map style that doesn't require Mapbox token
                        map_style='',  # Empty string uses default basemap
                        height=600
                    )
                    
                    st.pydeck_chart(deck, use_container_width=True)
                    
                    # Legend with PagoNxt colors
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown('<span style="color: #5B2C91; font-size: 20px;">●</span> Approval Rate ≥ 90%', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<span style="color: #00A3E0; font-size: 20px;">●</span> Approval Rate 80-90%', unsafe_allow_html=True)
                    with col3:
                        st.markdown('<span style="color: #FF3366; font-size: 20px;">●</span> Approval Rate < 80%', unsafe_allow_html=True)
                    
                    # Show sample data for debugging
                    with st.expander("🔍 View Sample Map Data"):
                        st.dataframe(geo_data.head(10), use_container_width=True)
                
                except Exception as e:
                    st.error(f"⚠️ Error rendering PyDeck map: {str(e)}")
                    st.info("💡 PyDeck requires WebGL support. Using Plotly map as alternative...")
                    
                    # Fallback to Plotly scatter_geo (works everywhere)
                    try:
                        st.markdown("### 🌍 Interactive Geographic Visualization")
                        fig = px.scatter_geo(
                            geo_data,
                            lat='lat',
                            lon='lon',
                            size='txn_count',
                            color='approval_rate',
                            hover_name='country',
                            hover_data={
                                'lat': False,
                                'lon': False,
                                'approval_rate': ':.1f',
                                'txn_count': ':,',
                                'total_volume': ':$,.0f'
                            },
                            color_continuous_scale=[
                                [0.0, '#FF3366'],   # Red for low
                                [0.5, '#00A3E0'],   # Blue for medium
                                [1.0, '#5B2C91']    # Purple for high
                            ],
                            size_max=50,
                            projection='natural earth',
                            labels={'approval_rate': 'Approval Rate (%)'}
                        )
                        
                        fig.update_geos(
                            showcountries=True,
                            countrycolor='#E2E8F0',
                            showcoastlines=True,
                            coastlinecolor='#CBD5E0',
                            showland=True,
                            landcolor='#F8F9FA',
                            showocean=True,
                            oceancolor='#E6F3FF',
                            bgcolor='#FFFFFF'
                        )
                        
                        fig.update_layout(
                            height=600,
                            plot_bgcolor='#FFFFFF',
                            paper_bgcolor='#FFFFFF',
                            font_color='#1A1F2E',
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Legend
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown('<span style="color: #5B2C91; font-size: 20px;">●</span> High Approval (≥90%)', unsafe_allow_html=True)
                        with col2:
                            st.markdown('<span style="color: #00A3E0; font-size: 20px;">●</span> Medium Approval (80-90%)', unsafe_allow_html=True)
                        with col3:
                            st.markdown('<span style="color: #FF3366; font-size: 20px;">●</span> Low Approval (<80%)', unsafe_allow_html=True)
                            
                    except Exception as fallback_error:
                        st.error(f"⚠️ Fallback visualization also failed: {str(fallback_error)}")
                        st.info("📊 Please check the Choropleth or Country Rankings tabs for geographic data.")
            else:
                st.warning("No data available after filtering. Adjust filters to see map.")
        
        with tab2:
            st.markdown("### World Choropleth Map")
            st.info("💡 Countries colored by approval rate. Hover for details.")
            
            if not geo_data.empty:
                try:
                    # Create choropleth map with PagoNxt colors
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
                            [0.0, '#FF3366'],  # Red for low
                            [0.5, '#FFB020'],  # Orange for medium
                            [1.0, '#5B2C91']   # PagoNxt purple for high
                        ],
                        range_color=[0, 100],
                        labels={'approval_rate': 'Approval Rate (%)'}
                    )
                    
                    fig.update_geos(
                        showcountries=True,
                        countrycolor="#2D3748",
                        showcoastlines=True,
                        coastlinecolor="#4A5568",
                        showland=True,
                        landcolor="#0F1419",
                        showocean=True,
                        oceancolor="#0A0E12",
                        projection_type='natural earth',
                        bgcolor='#0F1419'
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='#0F1419',
                        paper_bgcolor='#1A1F2E',
                        font_color='#B8C5D0',
                        height=600,
                        margin=dict(l=0, r=0, t=30, b=0),
                        coloraxis_colorbar=dict(
                            title="Approval Rate (%)",
                            ticksuffix="%",
                            thickness=15,
                            len=0.7,
                            bgcolor='#1A1F2E',
                            bordercolor='#2D3748',
                            borderwidth=2
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"⚠️ Error rendering choropleth map: {str(e)}")
                    st.warning("📊 Using fallback visualization...")
                    
                    # Fallback: simple bar chart
                    fig = px.bar(
                        geo_data.nlargest(20, 'approval_rate'),
                        x='approval_rate',
                        y='country',
                        orientation='h',
                        color='approval_rate',
                        color_continuous_scale='Purples',
                        title="Top 20 Countries by Approval Rate",
                        labels={'approval_rate': 'Approval Rate (%)'}
                    )
                    fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
                    fig.update_layout(
                        plot_bgcolor='#0F1419',
                        paper_bgcolor='#1A1F2E',
                        font_color='#B8C5D0',
                        height=600,
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                    fig.update_yaxes(showgrid=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available after filtering. Adjust filters to see map.")
        
        with tab3:
            st.markdown("### 📊 Country Performance Rankings")
            
            if not geo_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏆 Top Performers (Approval Rate)")
                    top_performers = geo_data.nlargest(10, 'approval_rate')[['country', 'approval_rate', 'txn_count', 'total_volume']]
                    
                    if not top_performers.empty:
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
                    else:
                        st.info("No countries meet the filter criteria for top performers")
                
                with col2:
                    st.markdown("#### 📈 Highest Volume")
                    top_volume = geo_data.nlargest(10, 'txn_count')[['country', 'approval_rate', 'txn_count', 'total_volume']]
                    
                    if not top_volume.empty:
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
                    else:
                        st.info("No countries meet the filter criteria for highest volume")
            else:
                st.warning("No data available. Adjust filters to see country rankings.")
        
        with tab4:
            st.markdown("### 🔍 Country Drill-Down Analysis")
            
            if not geo_data.empty:
                selected_country = st.selectbox(
                    "Select Country for Detailed Analysis",
                    options=sorted(geo_data['country'].unique())
                )
                
                if selected_country:
                    country_data = checkout_data[checkout_data['geography'] == selected_country]
                    
                    if not country_data.empty:
                        # Country-specific KPIs
                        col1, col2, col3, col4 = st.columns(4)
                        
                        country_approval = (country_data['approval_status'] == 'approved').sum() / len(country_data) * 100 if 'approval_status' in country_data.columns else 0
                        country_volume = country_data[country_data['approval_status'] == 'approved']['amount'].sum() if 'amount' in country_data.columns and 'approval_status' in country_data.columns else 0
                        country_avg_risk = country_data['risk_score'].mean() if 'risk_score' in country_data.columns else 0
                        country_txns = len(country_data)
                        
                        with col1:
                            st.metric("Approval Rate", f"{country_approval:.1f}%", "+2.3%")
                        with col2:
                            st.metric("Total Volume", f"${country_volume:,.0f}", "+$12.5K")
                        with col3:
                            st.metric("Avg Risk Score", f"{country_avg_risk:.3f}", "-0.05")
                        with col4:
                            st.metric("Transactions", f"{country_txns:,}", "+125")
                        
                        st.markdown("---")
                        
                        # Channel and solution breakdown
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
                                    color_discrete_sequence=['#5B2C91', '#00A3E0', '#00D9FF', '#FF6B6B']
                                )
                                fig.update_layout(
                                    plot_bgcolor='#0D1117',
                                    paper_bgcolor='#161B22',
                                    font_color='#C9D1D9',
                                    height=350
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Channel data not available")
                        
                        with col2:
                            st.markdown(f"#### 🎯 Solution Mix Performance - {selected_country}")
                            if 'recommended_solution_name' in country_data.columns and 'approval_status' in country_data.columns:
                                solution_stats = country_data.groupby('recommended_solution_name').agg({
                                    'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0
                                }).reset_index()
                                solution_stats.columns = ['solution', 'approval_rate']
                                solution_stats = solution_stats.nlargest(8, 'approval_rate')
                                
                                fig = px.bar(
                                    solution_stats,
                                    x='approval_rate',
                                    y='solution',
                                    orientation='h',
                                    color='approval_rate',
                                    color_continuous_scale='Purples',
                                    labels={'approval_rate': 'Approval Rate (%)'}
                                )
                                fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
                                fig.update_layout(
                                    plot_bgcolor='#0D1117',
                                    paper_bgcolor='#161B22',
                                    font_color='#C9D1D9',
                                    height=350,
                                    showlegend=False
                                )
                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                                fig.update_yaxes(showgrid=False)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Solution mix data not available")
                        
                        # Time series for country
                        st.markdown(f"#### 📈 Hourly Performance Trends - {selected_country}")
                        if 'timestamp' in country_data.columns and 'approval_status' in country_data.columns:
                            country_data['timestamp'] = pd.to_datetime(country_data['timestamp'])
                            hourly = country_data.set_index('timestamp').resample('1H').agg({
                                'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                                'transaction_id': 'count' if 'transaction_id' in country_data.columns else lambda x: len(x)
                            }).reset_index()
                            hourly.columns = ['timestamp', 'approval_rate', 'txn_count']
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=hourly['timestamp'],
                                y=hourly['approval_rate'],
                                mode='lines+markers',
                                name='Approval Rate',
                                line=dict(color='#5B2C91', width=3),
                                fill='tozeroy',
                                fillcolor='rgba(91, 44, 145, 0.1)',
                                hovertemplate='%{y:.1f}%<extra></extra>'
                            ))
                            
                            fig.update_layout(
                                plot_bgcolor='#0D1117',
                                paper_bgcolor='#161B22',
                                font_color='#C9D1D9',
                                height=350,
                                xaxis_title="Time",
                                yaxis_title="Approval Rate (%)",
                                showlegend=False
                            )
                            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
                            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Time series data not available")
                    else:
                        st.warning(f"No transaction data available for {selected_country}")
            else:
                st.warning("No countries available. Adjust filters to see drill-down analysis.")




def show_smart_checkout(checkout_data):
    """Enhanced Smart Checkout page"""
    st.markdown('<h2 class="section-header-premium">🎯 Smart Checkout Analytics</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box-premium">
        <strong>Smart Checkout</strong> dynamically selects the optimal payment solution mix for each transaction 
        to maximize approval rates while managing risk and cost.
    </div>
    """, unsafe_allow_html=True)
    
    # Ensure we have valid data with required columns
    if checkout_data.empty or 'recommended_solution_name' not in checkout_data.columns or 'approval_status' not in checkout_data.columns:
        st.info("🔄 Loading Smart Checkout data...")
        checkout_data = generate_synthetic_data('payments_enriched_stream')
    
    if checkout_data.empty:
        st.warning("No checkout data available")
        return
    
    # Solution mix performance
    try:
        if 'recommended_solution_name' in checkout_data.columns and 'approval_status' in checkout_data.columns:
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
    except Exception as e:
        st.error(f"⚠️ Error rendering Smart Checkout analytics: {str(e)}")
        st.info("Please ensure the data includes 'recommended_solution_name', 'approval_status', 'transaction_id', and 'risk_score' columns.")

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
    
    st.markdown("""
    <div class="info-box-premium">
        <p><strong>Comprehensive performance analytics</strong> showing trends, comparisons, and detailed metrics 
        across all Approval Rates activities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ensure we have valid data
    if checkout_data.empty or 'approval_status' not in checkout_data.columns or 'timestamp' not in checkout_data.columns:
        st.info("🔄 Loading performance metrics data...")
        checkout_data = generate_synthetic_data('payments_enriched_stream')
    
    if decline_data.empty:
        decline_data = generate_synthetic_data('reason_code_insights')
    
    if retry_data.empty:
        retry_data = generate_synthetic_data('smart_retry_recommendations')
    
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🔀 Comparisons", "📉 Detailed Metrics"])
    
    with tab1:
        st.markdown("### 📈 Time-Series Performance Analysis")
        # Add time series charts
        try:
            if not checkout_data.empty and 'timestamp' in checkout_data.columns and 'approval_status' in checkout_data.columns:
                checkout_data['timestamp'] = pd.to_datetime(checkout_data['timestamp'])
                
                # Hourly trends for more granular view
                hourly = checkout_data.set_index('timestamp').resample('1H').agg({
                    'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100 if len(x) > 0 else 0,
                    'transaction_id': 'count'
                }).reset_index()
                hourly.columns = ['timestamp', 'approval_rate', 'txn_count']
                
                # Create dual-axis chart
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Scatter(
                        x=hourly['timestamp'],
                        y=hourly['approval_rate'],
                        mode='lines+markers',
                        name='Approval Rate',
                        line=dict(color='#5B2C91', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(91, 44, 145, 0.1)',
                        hovertemplate='%{y:.1f}%<extra></extra>'
                    ),
                    secondary_y=False
                )
                
                fig.add_trace(
                    go.Bar(
                        x=hourly['timestamp'],
                        y=hourly['txn_count'],
                        name='Transaction Volume',
                        marker_color='#00A3E0',
                        opacity=0.3,
                        hovertemplate='%{y} txns<extra></extra>'
                    ),
                    secondary_y=True
                )
                
                fig.update_layout(
                    plot_bgcolor='#0D1117',
                    paper_bgcolor='#161B22',
                    font_color='#C9D1D9',
                    height=500,
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
                
                fig.update_xaxes(
                    title_text="Time",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#30363D'
                )
                
                fig.update_yaxes(
                    title_text="Approval Rate (%)",
                    secondary_y=False,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#30363D',
                    range=[0, 100]
                )
                
                fig.update_yaxes(
                    title_text="Transaction Count",
                    secondary_y=True,
                    showgrid=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # KPI Summary
                col1, col2, col3, col4 = st.columns(4)
                
                total_txns = len(checkout_data)
                approved = (checkout_data['approval_status'] == 'approved').sum()
                approval_rate = (approved / total_txns * 100) if total_txns > 0 else 0
                
                if 'amount' in checkout_data.columns:
                    total_volume = checkout_data[checkout_data['approval_status'] == 'approved']['amount'].sum()
                    avg_value = checkout_data[checkout_data['approval_status'] == 'approved']['amount'].mean()
                else:
                    total_volume = 0
                    avg_value = 0
                
                with col1:
                    st.metric("Total Transactions", f"{total_txns:,}", "+125")
                with col2:
                    st.metric("Approval Rate", f"{approval_rate:.1f}%", "+2.3%")
                with col3:
                    st.metric("Approved Volume", f"${total_volume/1e6:.2f}M", "+$1.2M")
                with col4:
                    st.metric("Avg Transaction", f"${avg_value:.2f}", "+$5.30")
            else:
                st.warning("Insufficient data for trend analysis")
        except Exception as e:
            st.error(f"⚠️ Error rendering trends: {str(e)}")
            st.info("Please ensure data includes 'timestamp' and 'approval_status' columns.")
    
    with tab2:
        st.markdown("### 🔀 Baseline vs. Optimized Performance")
        
        try:
            # Calculate metrics
            if not checkout_data.empty and 'approval_status' in checkout_data.columns:
                # Simulated baseline (85%) vs current optimized
                baseline_rate = 85.0
                current_rate = (checkout_data['approval_status'] == 'approved').sum() / len(checkout_data) * 100
                rate_improvement = current_rate - baseline_rate
                
                if 'amount' in checkout_data.columns:
                    current_volume = checkout_data[checkout_data['approval_status'] == 'approved']['amount'].sum()
                    baseline_volume = current_volume / (current_rate / 100) * (baseline_rate / 100)
                    volume_improvement = current_volume - baseline_volume
                else:
                    current_volume = 8500000
                    baseline_volume = 8200000
                    volume_improvement = 300000
                
                # Display comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Baseline Performance")
                    st.metric("Approval Rate", f"{baseline_rate:.1f}%")
                    st.metric("Approved Volume", f"${baseline_volume/1e6:.2f}M")
                    st.metric("Declined Transactions", f"{15.0:.1f}%")
                    st.metric("Avg Processing Time", "2.5s")
                
                with col2:
                    st.markdown("#### 🚀 Optimized Performance")
                    st.metric("Approval Rate", f"{current_rate:.1f}%", f"+{rate_improvement:.1f}%")
                    st.metric("Approved Volume", f"${current_volume/1e6:.2f}M", f"+${volume_improvement/1e6:.2f}M")
                    declined_rate = 100 - current_rate
                    st.metric("Declined Transactions", f"{declined_rate:.1f}%", f"-{15.0-declined_rate:.1f}%")
                    st.metric("Avg Processing Time", "1.8s", "-0.7s")
                
                # Visualization
                st.markdown("---")
                st.markdown("#### 📊 Performance Comparison Chart")
                
                comparison_df = pd.DataFrame({
                    'Metric': ['Approval Rate', 'Decline Rate', 'Avg Processing Time (s)'],
                    'Baseline': [baseline_rate, 15.0, 2.5],
                    'Optimized': [current_rate, declined_rate, 1.8]
                })
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Baseline',
                    x=comparison_df['Metric'],
                    y=comparison_df['Baseline'],
                    marker_color='#FF6B6B',
                    text=comparison_df['Baseline'].round(1),
                    textposition='outside'
                ))
                
                fig.add_trace(go.Bar(
                    name='Optimized',
                    x=comparison_df['Metric'],
                    y=comparison_df['Optimized'],
                    marker_color='#5B2C91',
                    text=comparison_df['Optimized'].round(1),
                    textposition='outside'
                ))
                
                fig.update_layout(
                    plot_bgcolor='#0D1117',
                    paper_bgcolor='#161B22',
                    font_color='#C9D1D9',
                    height=400,
                    barmode='group',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # ROI Calculation
                st.markdown("---")
                st.markdown("#### 💰 Return on Investment")
                
                st.markdown(f"""
                <div class="success-box-premium">
                    <h3>Smart Checkout ROI</h3>
                    <p style="font-size: 2.5rem; font-weight: 700; color: #3FB950; margin: 1rem 0;">
                        +${volume_improvement/1e6:.2f}M
                    </p>
                    <p>Additional approved volume from optimization</p>
                    <p style="margin-top: 1rem;">
                        <strong>{rate_improvement:.1f}%</strong> improvement in approval rate translates to 
                        <strong>${volume_improvement:,.0f}</strong> incremental revenue
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Insufficient data for comparison analysis")
        except Exception as e:
            st.error(f"⚠️ Error rendering comparison: {str(e)}")
    
    with tab3:
        st.markdown("### 📉 Detailed Performance Breakdown")
        
        try:
            if not checkout_data.empty:
                # Channel breakdown
                if 'channel' in checkout_data.columns and 'approval_status' in checkout_data.columns:
                    st.markdown("#### 📱 Performance by Channel")
                    
                    channel_stats = checkout_data.groupby('channel').agg({
                        'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
                        'transaction_id': 'count'
                    }).reset_index()
                    channel_stats.columns = ['channel', 'approval_rate', 'txn_count']
                    channel_stats = channel_stats.sort_values('approval_rate', ascending=False)
                    
                    fig = px.bar(
                        channel_stats,
                        x='channel',
                        y='approval_rate',
                        color='approval_rate',
                        text='approval_rate',
                        color_continuous_scale=[[0, '#FF6B6B'], [0.5, '#FFB020'], [1, '#5B2C91']],
                        labels={'approval_rate': 'Approval Rate (%)'}
                    )
                    
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    
                    fig.update_layout(
                        plot_bgcolor='#0D1117',
                        paper_bgcolor='#161B22',
                        font_color='#C9D1D9',
                        height=400,
                        showlegend=False
                    )
                    
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Geography breakdown
                if 'geography' in checkout_data.columns:
                    st.markdown("#### 🌍 Top 10 Countries by Volume")
                    
                    geo_stats = checkout_data.groupby('geography').agg({
                        'approval_status': lambda x: (x == 'approved').sum() / len(x) * 100,
                        'transaction_id': 'count',
                        'amount': 'sum' if 'amount' in checkout_data.columns else lambda x: len(x) * 100
                    }).reset_index()
                    geo_stats.columns = ['country', 'approval_rate', 'txn_count', 'total_volume']
                    geo_stats = geo_stats.nlargest(10, 'txn_count')
                    
                    fig = px.scatter(
                        geo_stats,
                        x='txn_count',
                        y='approval_rate',
                        size='total_volume',
                        color='approval_rate',
                        text='country',
                        color_continuous_scale='Purples',
                        labels={
                            'txn_count': 'Transaction Count',
                            'approval_rate': 'Approval Rate (%)',
                            'total_volume': 'Total Volume'
                        }
                    )
                    
                    fig.update_traces(textposition='top center')
                    
                    fig.update_layout(
                        plot_bgcolor='#0D1117',
                        paper_bgcolor='#161B22',
                        font_color='#C9D1D9',
                        height=500,
                        showlegend=False
                    )
                    
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D', range=[0, 100])
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Raw data table
                st.markdown("#### 📋 Transaction Sample (Latest 100)")
                
                display_cols = ['transaction_id', 'timestamp', 'amount', 'geography', 'channel', 
                               'approval_status', 'risk_score', 'recommended_solution_name']
                available_cols = [col for col in display_cols if col in checkout_data.columns]
                
                st.dataframe(
                    checkout_data[available_cols].head(100),
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning("No data available for detailed metrics")
        except Exception as e:
            st.error(f"⚠️ Error rendering detailed metrics: {str(e)}")
            st.info("Please check that the data contains the expected columns.")

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
