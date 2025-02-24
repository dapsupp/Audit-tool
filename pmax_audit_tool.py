import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

# Page configuration
st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

# Logging setup
logging.basicConfig(filename="pmax_audit_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_web_ui():
    """Runs the Streamlit UI for the PMax Audit Tool with all original features."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    # File uploader
    st.warning("⚠️ Ensure your CSV column headers are in row 1 and all numbers are formatted correctly.")
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")
                insights, df_processed = assess_product_performance(df)

                # Tabs
                tab1, tab2, tab3 = st.tabs(["📊 SKU Performance", "📂 Detected Columns", "🔍 Debugging"])

                # SKU Performance Tab
                with tab1:
                    st.subheader("📊 Key Metrics Overview")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Items", insights["total_item_count"])
                    with col2:
                        st.metric("Total Impressions", f"{insights['total_impressions']:,}")
                    with col3:
                        st.metric("Total Clicks", f"{insights['total_clicks']:,}")
                    with col4:
                        st.metric("Total Conversions", f"{insights['total_conversions']:,}")

                    # Pareto Law SKU Contribution
                    st.subheader("📈 Pareto Law: SKU Contribution Breakdown")
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
                    st.dataframe(sku_table, height=300)

                    # Pareto Chart
                    st.subheader("📊 SKU Contribution vs Revenue & ROAS")
                    fig = px.bar(
                        sku_table,
                        x="SKU Tier",
                        y="Revenue Contribution (%)",
                        text="Revenue Contribution (%)",
                        title="SKU Contribution vs Revenue & ROAS",
                        color="Revenue Contribution (%)",
                        color_continuous_scale="Blues",
                        width=700,
                        height=300
                    )
                    fig.update_traces(texttemplate='%{text}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

                    # New Marketing Funnel Section
                    st.subheader("📊 Marketing Funnel Efficiency")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Impressions per Click**")
                        st.write(f"Average: {insights['avg_impressions_per_click']:.2f}")
                        st.write(f"Products Meeting Average: {insights['num_products_meeting_impressions']} ({insights['percent_meeting_impressions']:.2f}%)")
                    with col2:
                        st.write("**Clicks per Conversion**")
                        st.write(f"Average: {insights['avg_clicks_per_conversion']:.2f}")
                        st.write(f"Products Meeting Average: {insights['num_products_meeting_clicks']} ({insights['percent_meeting_clicks']:.2f}%)")

                # Detected Columns Tab
                with tab2:
                    st.subheader("📂 Detected Columns")
                    st.write(df_processed.columns.tolist())

                # Debugging Tab
                with tab3:
                    st.subheader("🔍 Debugging")
                    st.write("Processed DataFrame Sample:")
                    st.dataframe(df_processed.head())

            except Exception as e:
                logging.error(f"❌ Error: {e}")
                st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    run_web_ui()
