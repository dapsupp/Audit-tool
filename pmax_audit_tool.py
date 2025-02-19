import streamlit as st
import pandas as pd
from data_processing import assess_product_performance
import logging

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

                # ✅ **1. Detected Columns**
                logging.info(f"📂 Detected Columns: {df.columns.tolist()}")
                st.subheader("📂 Detected Columns")
                st.write(df.columns.tolist())

                # Process data
                insights, df_processed = assess_product_performance(df)

                # ✅ **2. Debugging: Raw Insights Output**
                st.subheader("🔍 Debugging: Raw Insights Output")
                st.write(insights)

                # ✅ **3. Summary Metrics**
                if insights:
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

                # ✅ **4. Pareto Law Insights (New Section)**
                st.subheader("📈 Pareto Law Insights")
                pareto_df = pd.DataFrame([{
                    "Top SKUs Count (80% of Sales)": f"{insights['top_skus_count']}",
                    "Top SKUs Contribution (%)": f"{insights['top_skus_percentage']:.2f}%",
                    "Top 5% SKU Contribution": f"{insights['top_5_sku_contribution']}%",
                    "Top 10% SKU Contribution": f"{insights['top_10_sku_contribution']}%",
                    "Top 20% SKU Contribution": f"{insights['top_20_sku_contribution']}%",
                    "Top 50% SKU Contribution": f"{insights['top_50_sku_contribution']}%",
                    "High ROAS but Low Spend SKUs": f"{insights['high_roas_low_spend_count']}",
                    "Low ROAS but High Spend SKUs": f"{insights['low_roas_high_spend_count']}",
                    "Long-Tail SKUs (<1% Revenue)": f"{insights['low_performing_sku_count']}",
                }])

                st.dataframe(pareto_df)

                # ✅ **5. Processed Data Preview**
                st.subheader("📂 Processed Data Preview")
                st.dataframe(df_processed, height=600)

                # ✅ Download Processed Data
                st.download_button(
                    label="📥 Download Processed Data",
                    data=df_processed.to_csv(index=False).encode('utf-8'),
                    file_name="processed_data.csv",
                    mime="text/csv"
                )

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
