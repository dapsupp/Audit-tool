import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

# ✅ Ensure this is the first Streamlit command
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# ✅ Configure logging
logging.basicConfig(
    filename="pmax_audit_tool.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    # File uploader
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="warn")
                insights, df_processed = assess_product_performance(df)

                # ✅ Ensure all required keys exist
                required_keys = [
                    "total_conversion_value", "total_cost", "roas",
                    "total_clicks", "total_item_count", "total_impressions",
                    "average_ctr", "average_search_impression_share",
                    "total_conversions"
                ]
                for key in required_keys:
                    insights.setdefault(key, 0)

                # ✅ Validate and log missing SKU contribution data
                sku_tiers = [5, 10, 20, 50]
                for threshold in sku_tiers:
                    key = f"top_{threshold}_sku_contribution"
                    if key not in insights:
                        logging.warning(f"Missing SKU contribution data for {key}")
                        insights[key] = {
                            "sku_count": 0,
                            "percentage": 0,
                            "conversion_value": 0,
                            "roas": 0
                        }

                logging.info(f"Insights Dictionary: {insights.keys()}")

                # ✅ Define application tabs
                tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "📈 SKU Breakdown", "🔍 Debugging"])

                # 🔴 Restore Performance Metrics
                with tab1:
                    st.subheader("📊 Key Metrics Overview")

                    # ✅ Grid layout
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Total Conversion Value", f"£{insights['total_conversion_value']:,.2f}")
                    col2.metric("💸 Total Cost", f"£{insights['total_cost']:,.2f}")
                    col3.metric("⚡ ROAS", f"{insights['roas']:.2f}")

                    col4, col5, col6 = st.columns(3)
                    col4.metric("🖱️ Total Clicks", f"{insights['total_clicks']:,}")
                    col5.metric("🔍 Avg Search Impression Share", f"{insights['average_search_impression_share']:.2f}%")
                    col6.metric("📊 Average CTR", f"{insights['average_ctr']:.2f}%")

                # 🔴 Restore SKU Breakdown
                with tab2:
                    st.subheader("📈 SKU Contribution Breakdown")

                    # ✅ Define SKU Contribution Data
                    sku_data = []
                    for threshold in sku_tiers:
                        key = f"top_{threshold}_sku_contribution"
                        sku_data.append({
                            "SKU Tier": f"Top {threshold}%",
                            "Number of SKUs": f"{insights[key]['sku_count']:,}",
                            "Revenue Contribution (%)": f"{insights[key]['percentage']}%",
                            "Total Conversion Value (£)": f"£{insights[key]['conversion_value']:,.2f}",
                            "ROAS": f"{insights[key]['roas']:.2f}"
                        })

                    # ✅ Display SKU Contribution Table & Chart
                    sku_table = pd.DataFrame(sku_data)
                    st.dataframe(sku_table, height=300)

                    # 🔵 Restore SKU Contribution Graph
                    st.subheader("📊 SKU Contribution vs Revenue & ROAS")
                    fig = px.bar(
                        sku_table,
                        x="SKU Tier",
                        y="Revenue Contribution (%)",
                        text="Revenue Contribution (%)",
                        title="SKU Contribution vs Revenue & ROAS",
                        color="Revenue Contribution (%)",
                        color_continuous_scale="Blues",
                        height=400
                    )
                    fig.update_traces(texttemplate='%{text}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

                # 🔍 Debugging Tab
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
