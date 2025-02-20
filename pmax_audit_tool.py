import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

logging.basicConfig(filename="pmax_audit_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="warn")
                insights, df_processed = assess_product_performance(df)

                required_keys = ["total_conversion_value", "total_cost", "roas"]
                for key in required_keys:
                    insights.setdefault(key, 0)

                tab1, tab2 = st.tabs(["📊 Performance Overview", "🔍 Debugging"])

                with tab1:
                    st.subheader("📊 Key Metrics Overview")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Total Conversion Value", f"£{insights['total_conversion_value']:,.2f}")
                    col2.metric("💸 Total Cost", f"£{insights['total_cost']:,.2f}")
                    col3.metric("⚡ ROAS", f"{insights['roas']:.2f}")

                with tab2:
                    st.subheader("🔍 Debugging: Raw Insights Output")
                    st.write(insights)

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
