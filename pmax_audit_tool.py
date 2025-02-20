import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")

                # Process data to extract insights
                insights, df_processed = assess_product_performance(df)

                # ✅ Debugging: Ensure the displayed ROAS matches the computed ROAS
                print(f"DEBUG - Displayed ROAS: {insights['roas']}")

                # ✅ Ensure ROAS is pulled directly from insights
                metrics = [
                    {"label": "⚡ ROAS (Return on Ad Spend)", "value": f"{insights['roas']}"},
                ]

                st.subheader("📊 Key Metrics Overview")
                row1 = st.columns(3)

                for col, metric in zip(row1, metrics):
                    col.metric(metric["label"], metric["value"])

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
