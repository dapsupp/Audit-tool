import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

# Configure logging
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_web_ui():
    """Creates an enterprise-grade UI for PMax Audit Tool."""
    st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    # **New UI Message**
    st.warning("⚠️ **Ensure your CSV column headers are in row 1 and all numbers are formatted correctly.**")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                # Handle encoding variations
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1", on_bad_lines="skip")

                # Process data
                insights, df_processed = assess_product_performance(df)

                # ✅ **Tab Structure**
                tab1, tab2, tab3 = st.tabs(["📊 SKU Performance", "📂 Detected Columns", "🔍 Debugging"])

                # 🟢 **TAB 1: SKU PERFORMANCE (Main Dashboard)**
                with tab1:
                    # Two-column layout for Summary & Pareto Insights
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📊 Summary Metrics")
                        summary_df = pd.DataFrame([{
                            "Total Items": insights["total_item_count"],
                            "Total Impressions": f"{insights['total_impressions']:,}",
                            "Total Clicks": f"{insights['total_clicks']:,}",
                            "Average CTR": f"{insights['average_ctr']:.2f}%",
                            "Total Conversions": f"{insights['total_conversions']:,}",
                            "Total Conversion Value": f"£{insights['total_conversion_value']:.2f}",
                            "Total Cost": f"£{insights['total_cost']:.2f}",
                            "Average Search Impression Share": f"{insights['average_search_impression_share']:.2f}%",
                            "ROAS (Conv. Value / Cost)": f"{insights['roas']:.2f}",
                        }])
                        st.dataframe(summary_df)

                    with col2:
                        st.subheader("📈 Pareto Law Insights")
                        sku_tiers = [5, 10, 20, 50]
                        sku_table = pd.DataFrame([
                            {
                                "SKU Tier": f"Top {threshold}%",
                                "Number of SKUs": f"{insights[f'top_{threshold}_sku_contribution']['sku_count']:,}",
                                "Revenue Contribution (%)": f"{insights[f'top_{threshold}_sku_contribution']['percentage']}%",
                                "Total Conversion Value (£)": f"£{insights[f'top_{threshold}_sku_contribution']['conversion_value']:,}",
                                "ROAS": f"{insights[f'top_{threshold}_sku_contribution']['roas']:.2f}",
                            }
                            for threshold in sku_tiers
                        ])
                        st.dataframe(sku_table)

                    # ✅ **Graph Section - Now Using Plotly**
                    st.subheader("📊 SKU Contribution vs Revenue & ROAS")

                    fig = px.bar(
                        sku_table, 
                        x="SKU Tier", 
                        y="Revenue Contribution (%)", 
                        text="Revenue Contribution (%)", 
                        title="SKU Contribution vs Revenue & ROAS",
                        color="Revenue Contribution (%)",
                        color_continuous_scale="Blues"
                    )

                    fig.update_traces(texttemplate='%{text}%', textposition='outside')

                    # ✅ Auto-Resizes to Fit Streamlit Container
                    st.plotly_chart(fig, use_container_width=True)

                # 🟢 **TAB 2: DETECTED COLUMNS (Mapping + Processed Data)**
                with tab2:
                    st.subheader("📂 Detected Columns")
                    st.write(df.columns.tolist())

                    st.subheader("📂 Processed Data Preview")
                    st.dataframe(df_processed, height=600)

                    st.download_button(
                        label="📥 Download Processed Data",
                        data=df_processed.to_csv(index=False).encode('utf-8'),
                        file_name="processed_data.csv",
                        mime="text/csv"
                    )

                # 🟢 **TAB 3: DEBUGGING (Raw Insights)**
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
