import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
                st.subheader("📈 Pareto Law Insights: SKU Contribution Breakdown")

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

                st.table(sku_table)

                # ✅ Visualization: SKU Contribution vs Revenue & ROAS
                fig, ax1 = plt.subplots(figsize=(10, 6))

                # Bar plot for Revenue Contribution (%)
                sns.barplot(
                    x=sku_table["SKU Tier"],
                    y=pd.to_numeric(sku_table["Revenue Contribution (%)"].str.replace('%', ''), errors='coerce'),
                    palette="Blues_d",
                    ax=ax1
                )

                ax1.set_ylabel("Revenue Contribution (%)", color="blue")
                ax1.set_xlabel("SKU Tier")
                ax1.set_title("SKU Contribution: Revenue vs ROAS")
                ax1.set_ylim(0, 110)

                # Create secondary Y-axis for ROAS
                ax2 = ax1.twinx()
                sns.lineplot(
                    x=sku_table["SKU Tier"],
                    y=pd.to_numeric(sku_table["ROAS"], errors='coerce'),
                    color="red",
                    marker="o",
                    linewidth=2,
                    ax=ax2
                )

                ax2.set_ylabel("ROAS", color="red")
                ax2.set_ylim(0, max(pd.to_numeric(sku_table["ROAS"], errors='coerce')) + 1)

                # Display the plot
                st.pyplot(fig)

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
