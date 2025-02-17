import streamlit as st
import tempfile
import pandas as pd
import logging

from auth import get_authenticator
from data_processing import process_large_csv
from charts import create_metrics_bar_chart, create_pareto_chart

# Set up the page configuration
st.set_page_config(page_title="PMax Audit Dashboard", layout="wide")

# Authenticate the user
authenticator = get_authenticator()
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.title(f"Welcome, {name}")
    authenticator.logout("Logout", "sidebar")
    
    st.title("📊 PMax Audit Dashboard")
    st.write("Analyse your Performance Max campaign data efficiently without file size limits.")
    st.markdown(
        """
        ## 🔹 Expected CSV Column Order
        | # | Column |
        |---|------------------------------|
        | 1 | Item ID |
        | 2 | Impressions (Impr.) |
        | 3 | Clicks |
        | 4 | Click-Through Rate (CTR) |
        | 5 | Conversions |
        | 6 | Conversion Value (Conv. value) |
        | 7 | Cost |
        | 8 | Conversion Value / Cost (ROAS) |
        | 9 | Search Impression Share |
        """
    )
    
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")
    if uploaded_file:
        with st.spinner("Processing file..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name
            try:
                insights, sku_sales = process_large_csv(tmp_file_path)
                if insights:
                    st.subheader("📊 Summary Metrics")
                    summary_df = pd.DataFrame({
                        "Metric": list(insights.keys()),
                        "Value": list(insights.values())
                    })
                    st.table(summary_df)
                    
                    st.subheader("📈 Visual Overview")
                    metrics_fig = create_metrics_bar_chart(insights)
                    st.plotly_chart(metrics_fig, use_container_width=True)
                    
                    if sku_sales and insights.get("Total Conversion Value", 0) > 0:
                        st.subheader("📉 Pareto Analysis")
                        pareto_fig = create_pareto_chart(sku_sales, insights["Total Conversion Value"])
                        st.plotly_chart(pareto_fig, use_container_width=True)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.error(f"Error in main.py: {e}")
else:
    if authentication_status is False:
        st.error("Username/password is incorrect")
    else:
        st.warning("Please enter your username and password")
