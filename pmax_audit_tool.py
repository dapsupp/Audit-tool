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

                insights = assess_product_performance(df)

                # ✅ SKU Contribution Breakdown Table
                st.subheader("📈 SKU Contribution Breakdown (Revenue & ROAS)")

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

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
