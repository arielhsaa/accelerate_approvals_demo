"""
ULTRA-MINIMAL TEST APP - For Databricks Troubleshooting
Purpose: Test if Streamlit can start AT ALL in your Databricks environment
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """Absolute minimal working app"""
    
    # FIRST: Set page config
    st.set_page_config(
        page_title="Databricks Test",
        page_icon="✅",
        layout="wide"
    )
    
    # Simple styling
    st.markdown("""
    <style>
        .main { background-color: #1A1A1A; }
        h1 { color: #EC0000; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("✅ Streamlit Test - Ultra Minimal")
    
    # Success indicator
    st.success("🎉 SUCCESS! Streamlit is working in Databricks!")
    
    # Current time
    st.write(f"**Current time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Simple dataframe
    df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Value': [10, 20, 30, 40, 50],
        'Status': ['OK', 'OK', 'OK', 'OK', 'OK']
    })
    
    st.subheader("Test Data")
    st.dataframe(df)
    
    # Simple calculation
    st.subheader("Simple Calculation")
    total = df['Value'].sum()
    st.metric("Total", total)
    
    # Info message
    st.info("If you see this page, Streamlit is running correctly!")
    
    st.divider()
    st.caption("Test version - No pydeck, no plotly, no pyspark")

if __name__ == "__main__":
    main()
