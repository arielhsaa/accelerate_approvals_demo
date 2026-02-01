"""
Minimal test version of the app to verify Streamlit starts correctly in Databricks
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """Minimal main function for testing"""
    
    # MUST BE FIRST STREAMLIT COMMAND
    st.set_page_config(
        page_title="Payment Authorization Test",
        page_icon="💳",
        layout="wide"
    )
    
    # Simple CSS
    st.markdown("""
    <style>
        .main { background-color: #1A1A1A; color: white; }
        h1 { color: #EC0000; }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple content
    st.title("💳 Payment Authorization - Test Mode")
    st.success("✅ App started successfully!")
    
    st.write(f"Current time: {datetime.now()}")
    
    # Generate simple test data
    df = pd.DataFrame({
        'transaction_id': range(1, 11),
        'amount': np.random.randint(10, 1000, 10),
        'status': np.random.choice(['approved', 'declined'], 10)
    })
    
    st.subheader("Test Data")
    st.dataframe(df)
    
    st.info("If you see this, Streamlit is working correctly!")

if __name__ == "__main__":
    main()
