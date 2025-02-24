import streamlit as st
import pandas as pd
import plotly.express as px
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
                
                # Check for required columns
                required_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'cost']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    st.warning(f"⚠️ Missing columns in CSV: {', '.join(missing_columns)}. Some features may not work as expected.")
                
                # Process data to extract insights
                insights, df_processed = assess_product_performance(df)
                
                # Debugging: display insights keys
                st.write("Insights keys:", list(insights.keys()))
                
                # Define application tabs
                tab1, tab2, tab3 = st.tabs(["📊 SKU Performance", "📂 Detected Columns", "🔍 Debugging"])

                # SKU Performance Tab
                with tab1:
                    st.subheader("📊 Key Metrics Overview")

                    # Define Key Performance Metrics
                    metrics = [
                        {"label": "🛍️ Total Items", "value": f"{insights['total_item_count']:,}"},
                        {"label": "📈 Total Impressions", "value": f"{insights['total_impressions']:,}"},
                        {"label": "🏆 Average CTR", "value": f"{insights['average_ctr']:.2f}%" if 'average_ctr' in insights else "N/A"},
                        {"label": "💰 Total Conversion Value", "value": f"£{insights['total_conversion_value']:,.2f}"},
                        {"label": "🔍 Search Impression Share", "value": f"{insights['average_search_impression_share']:.2f}%"},
                        {"label": "⚡ ROAS", "value": f"{insights['roas']:.2f}"},
                        {"label": "🖱️ Total Clicks", "value": f"{insights['total_clicks']:,}"},
                        {"label": "💸 Total Cost", "value": f"£{insights['total_cost']:,.2f}"},
                        {"label": "🔄 Total Conversions", "value": f"{insights['total_conversions']:,}"},
                    ]

                    # Create a 3x3 grid layout
                    row1 = st.columns(3)
                    st.markdown("<br>", unsafe_allow_html=True)
                    row2 = st.columns(3)
                    st.markdown("<br>", unsafe_allow_html=True)
                    row3 = st.columns(3)

                    # Card styling
                    card_style = """
                        <div style="
                            background-color: #1E1E1E; 
                            padding: 20px; 
                            border-radius: 10px; 
                            text-align: center; 
                            box-shadow: 0px 4px 8px rgba(255, 255, 255, 0.2);
                            color: white; 
                            font-size: 18px;
                            font-weight: bold;
                            width: 100%;
                            min-height: 120px;
                            margin: 5px 0 15px 0;
                        ">
                            <h3 style="color: white;">{}</h3>
                            <p style="font-size: 30px; margin: 5px 0;">{}</p>
                        </div>
                    """

                    # Assign metrics to rows
                    for col, metric in zip(row1, metrics[:3]):
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)
                    for col, metric in zip(row2, metrics[3:6]):
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)
                    for col, metric in zip(row3, metrics[6:]):
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)

                    # Marketing Funnel Section
                    st.subheader("📊 Marketing Funnel")
                    impressions_per_click = insights.get('overall_impressions_per_click', 0)
                    clicks_per_conversion = insights.get('overall_clicks_per_conversion', 0)
                    funnel_metrics = [
                        {"label": "📊 Avg. Impressions per Click", "value": f"{impressions_per_click:.2f}" if impressions_per_click > 0 else "N/A"},
                        {"label": "📊 Avg. Clicks per Conversion", "value": f"{clicks_per_conversion:.2f}" if clicks_per_conversion > 0 else "N/A"},
                    ]
                    funnel_row = st.columns(2)
                    for col, metric in zip(funnel_row, funnel_metrics):
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)

                    # SKU Contribution Breakdown (Pareto Law)
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

                    # SKU Contribution Graph
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

                # Detected Columns Tab
                with tab2:
                    st.subheader("📂 Detected Columns")
                    st.write(df.columns.tolist())

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
