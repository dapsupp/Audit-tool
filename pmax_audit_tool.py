import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance
from charts import plot_chart

# Set page configuration
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# Configure logging for error tracking
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@st.cache_data
def load_and_process_data(uploaded_file):
    """Load and process CSV file with caching for performance."""
    df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")
    insights, df_processed = assess_product_performance(df)
    return insights, df_processed

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")
    st.warning("⚠️ Ensure your CSV column headers are in row 1 and all numbers are formatted correctly.")
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                insights, df_processed = load_and_process_data(uploaded_file)

                tab1, tab2, tab3 = st.tabs(["📊 SKU Performance", "📂 Detected Columns", "🔍 Debugging"])
                with tab1:
                    st.subheader("📊 Key Metrics Overview")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Items", insights["total_item_count"])
                    col2.metric("Total Impressions", f"{insights['total_impressions']:,}")
                    col3.metric("Total Clicks", f"{insights['total_clicks']:,}")
                    col4.metric("Total Conversions", f"{insights['total_conversions']:,}")
                    col1.metric("Total Conversion Value", f"${insights['total_conversion_value']:,.2f}")
                    col2.metric("Total Cost", f"${insights['total_cost']:,.2f}")
                    col3.metric("Avg Search Impr. Share", f"{insights['average_search_impression_share']}%")
                    col4.metric("Avg CTR", f"{insights['average_ctr']}%")
                    st.metric("ROAS", f"{insights['roas']:.2f}x")

                    # Custom Metric Chart
                    st.subheader("📊 Custom Metric Chart")
                    metric = st.selectbox("Select Metric", ["impressions", "clicks", "conversions"])
                    if 'item_id' in df_processed.columns and metric in df_processed.columns:
                        fig = plot_chart(df_processed, metric)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"⚠️ Cannot plot chart: Missing 'item_id' or '{metric}'.")

                with tab2:
                    st.subheader("📂 Detected Columns")
                    st.write("Below are the columns detected in your uploaded CSV:")
                    st.write(df_processed.columns.tolist())

                with tab3:
                    st.subheader("🔍 Debugging Information")
                    st.write("Check the log file `pmax_audit_tool.log` for detailed debugging info.")
                    st.write("Processed DataFrame Head:")
                    st.write(df_processed.head())

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
