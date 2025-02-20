import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from data_processing import assess_product_performance

# Set page configuration
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# Configure logging for error tracking
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    # Display file upload section
    st.warning("⚠️ Ensure your CSV column headers are in row 1 and all numbers are formatted correctly.")
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")

                # Process data to extract insights
                insights, df_processed = assess_product_performance(df)

                # Define application tabs
                tab1, tab2, tab3 = st.tabs(["📊 SKU Performance", "📂 Detected Columns", "🔍 Debugging"])

                # SKU Performance Tab
                with tab1:
                    st.subheader("📊 Key Metrics Overview")

                    # ✅ Ensure funnel metrics exist before displaying
                    if "avg_impressions_per_click" in insights:
                        st.subheader("📉 Full-Funnel Performance")
                        col1, col2 = st.columns(2)
                        col1.metric("📊 Avg Impressions per Click", f"{insights['avg_impressions_per_click']:,}")
                        col2.metric("🔍 Products Meeting Impressions-to-Click Rate", f"{insights['num_products_meeting_impressions_per_click']}")

                        col3, col4 = st.columns(2)
                        col3.metric("📊 Avg Clicks per Conversion", f"{insights['avg_clicks_per_conversion']:,}")
                        col4.metric("🔍 Products Meeting Clicks-to-Conversion Rate", f"{insights['num_products_meeting_clicks_per_conversion']}")

                        # ✅ Funnel Chart Visualization
                        funnel_fig = go.Figure(go.Funnel(
                            y=["Impressions", "Clicks", "Conversions"],
                            x=[
                                df_processed["impressions"].sum(),
                                df_processed["clicks"].sum(),
                                df_processed["conversions"].sum()
                            ],
                            textinfo="value+percent initial",
                        ))

                        funnel_fig.update_layout(title="📉 Funnel View: Impressions → Clicks → Conversions")
                        st.plotly_chart(funnel_fig, use_container_width=True)

                # Debugging Tab
                with tab3:
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
