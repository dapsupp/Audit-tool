import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

# ✅ Ensure `st.set_page_config()` is the first Streamlit command
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# Configure logging
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_web_ui():
    """Creates an enterprise-grade UI for PMax Audit Tool."""

    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    # **New UI Message**
    st.warning("⚠️ **Ensure your CSV column headersimport streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import logging
from data_processing import assess_product_performance

# ✅ Ensure `st.set_page_config()` is the first Streamlit command
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# Configure logging
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_web_ui():
    """Creates an enterprise-grade UI for PMax Audit Tool."""

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
                    st.subheader("📊 Key Metrics Overview")

                    # ✅ Define Metrics List
                    metrics = [
                        {"label": "🛍️ Total Items", "value": f"{insights['total_item_count']:,}"},
                        {"label": "📈 Total Impressions", "value": f"{insights['total_impressions']:,}"},
                        {"label": "📊 Average CTR", "value": f"{insights['average_ctr']:.2f}%"},
                        {"label": "💰 Total Conversion Value", "value": f"£{insights['total_conversion_value']:.2f}"},
                        {"label": "🔍 Search Impression Share", "value": f"{insights['average_search_impression_share']:.2f}%"},
                        {"label": "⚡ ROAS (Return on Ad Spend)", "value": f"{insights['roas']:.2f}"},
                    ]

                    # ✅ Inject Custom HTML + CSS for Modern Grid-Based Layout
                    html_content = """
                    <style>
                        .metric-container {
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 20px;
                            justify-content: center;
                            align-items: center;
                            width: 80%;
                            margin: auto;
                        }
                        .metric-card {
                            background-color: #1E1E1E;
                            padding: 20px;
                            border-radius: 10px;
                            text-align: center;
                            box-shadow: 0px 4px 8px rgba(255, 255, 255, 0.2);
                            color: white;
                            font-size: 18px;
                            font-weight: bold;
                            min-height: 120px;
                        }
                    </style>
                    <div class="metric-container">
                    """

                    for metric in metrics:
                        html_content += f'<div class="metric-card"><h3>{metric["label"]}</h3><p style="font-size: 30px;">{metric["value"]}</p></div>'

                    html_content += "</div>"

                    components.html(html_content, height=300)  # ✅ Embeds the modern grid layout

                # ✅ **Everything Else (Pareto Law Table, Graph, Debugging) Remains Unchanged**
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

                st.subheader("📈 Pareto Law: SKU Contribution Breakdown")
                st.dataframe(sku_table, height=300)

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
