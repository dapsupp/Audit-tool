import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from data_processing import assess_product_performance

def run_web_ui():
    """Initializes the Streamlit web UI for the PMax Audit Tool."""
    
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")

                # Process data to extract insights
                insights, df_processed = assess_product_performance(df)

                # ✅ Debugging: Ensure all key metrics exist before displaying
                print(f"DEBUG - Insights Dictionary: {insights.keys()}")

                # ✅ Ensure all key metrics are displayed
                metrics = [
                    {"label": "🛍️ Total Items", "value": f"{insights['total_item_count']:,}"},
                    {"label": "📈 Total Impressions", "value": f"{insights['total_impressions']:,}"},
                    {"label": "📊 Average CTR", "value": f"{insights['average_ctr']:.2f}%"},
                    {"label": "💰 Total Conversion Value", "value": f"£{insights['total_conversion_value']:,.2f}"},
                    {"label": "🔍 Search Impression Share", "value": f"{insights['average_search_impression_share']:.2f}%"},
                    {"label": "⚡ ROAS (Return on Ad Spend)", "value": f"{insights['roas']:.2f}"},
                    {"label": "🖱️ Total Clicks", "value": f"{insights['total_clicks']:,}"},
                    {"label": "💸 Total Cost", "value": f"£{insights['total_cost']:,.2f}"},
                    {"label": "🔄 Total Conversions", "value": f"{insights['total_conversions']:,}"},
                ]

                st.subheader("📊 Key Metrics Overview")
                row1 = st.columns(3)
                row2 = st.columns(3)
                row3 = st.columns(3)

                for col, metric in zip(row1, metrics[:3]):
                    col.metric(metric["label"], metric["value"])

                for col, metric in zip(row2, metrics[3:6]):
                    col.metric(metric["label"], metric["value"])

                for col, metric in zip(row3, metrics[6:]):
                    col.metric(metric["label"], metric["value"])

                # ✅ SKU Contribution Breakdown (Pareto Law)
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

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
