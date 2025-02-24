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

                    # Define Key Performance Metrics Including the New Row
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

                    # Create a Proper 3x3 Grid Layout
                    row1 = st.columns(3)  # First row (3 cards)
                    st.markdown("<br>", unsafe_allow_html=True)  # Adds Space Between Rows
                    row2 = st.columns(3)  # Second row (3 cards)
                    st.markdown("<br>", unsafe_allow_html=True)  # Adds Space Between Rows
                    row3 = st.columns(3)  # Third row (3 cards)

                    # Define Consistent Card Styling
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

                    # Assign Metrics to Rows to Ensure Proper Alignment
                    for col, metric in zip(row1, metrics[:3]):  # First row (Top 3 metrics)
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)

                    for col, metric in zip(row2, metrics[3:6]):  # Second row (Middle 3 metrics)
                        col.markdown(card_style.format(metric["label"], metric["value"]), unsafe_allow_html=True)

                    for col, metric in zip(row3, metrics[6:]):  # Third row (Newly Added 3 metrics)
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
                    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)

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
                    st.plotly_chart(fig, use_container_width=False)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # New Marketing Funnel Insights Section
                    st.markdown("### 📊 Marketing Funnel Insights")
                    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

                    # Interactive Summary
                    with st.expander("📋 Performance Summary", expanded=True):
                        if insights['ipc_low_percent'] > 50 or insights['cpc_low_percent'] > 50:
                            st.markdown(
                                "<div style='background-color: #FFF3E0; padding: 10px; border-radius: 5px;'>"
                                "⚠️ <b>Attention Needed</b>: High number of low-performing products detected.</div>",
                                unsafe_allow_html=True
                            )
                            st.write("Consider focusing on underperforming areas below.")
                        else:
                            st.markdown(
                                "<div style='background-color: #E6FFE6; padding: 10px; border-radius: 5px;'>"
                                "✅ <b>Good Performance</b>: Campaigns are generally efficient.</div>",
                                unsafe_allow_html=True
                            )
                            st.write("Maintain momentum and explore optimization opportunities.")

                    # Key Metrics with Enhanced Styling
                    col1, col2 = st.columns([1, 1], gap="medium")
                    with col1:
                        st.metric(
                            label="Avg Impressions per Click",
                            value=f"{insights['avg_impressions_per_click']:.2f}",
                            delta="Stable" if insights['std_impressions_per_click'] < 1 else "High Variance",
                            delta_color="normal" if insights['std_impressions_per_click'] < 1 else "inverse"
                        )
                        st.markdown(
                            "<span title='Number of impressions needed per click. Lower is better.'>ℹ️</span>",
                            unsafe_allow_html=True
                        )
                    with col2:
                        st.metric(
                            label="Avg Clicks per Conversion",
                            value=f"{insights['avg_clicks_per_conversion']:.2f}",
                            delta="Stable" if insights['std_clicks_per_conversion'] < 1 else "High Variance",
                            delta_color="normal" if insights['std_clicks_per_conversion'] < 1 else "inverse"
                        )
                        st.markdown(
                            "<span title='Number of clicks needed per conversion. Lower is better.'>ℹ️</span>",
                            unsafe_allow_html=True
                        )

                    # Performance Breakdown with Toggle
                    st.markdown("#### Performance Distribution")
                    view_option = st.radio("View as:", ("Count", "Percentage"), horizontal=True)

                    col3, col4 = st.columns([1, 1], gap="medium")

                    with col3:
                        st.write("**Impressions per Click**")
                        ipc_data = pd.DataFrame({
                            'Category': ['High', 'Moderate', 'Low'],
                            'Count': [insights['ipc_high_count'], insights['ipc_moderate_count'], insights['ipc_low_count']],
                            'Percentage': [insights['ipc_high_percent'], insights['ipc_moderate_percent'], insights['ipc_low_percent']]
                        })
                        y_axis = 'Count' if view_option == "Count" else 'Percentage'
                        fig_ipc = px.bar(
                            ipc_data,
                            x=y_axis,
                            y='Category',
                            orientation='h',
                            color='Category',
                            color_discrete_map={'High': '#00CC96', 'Moderate': '#FFD700', 'Low': '#EF553B'},
                            text=ipc_data[y_axis].apply(lambda x: f"{x:.1f}{'%' if y_axis == 'Percentage' else ''}"),
                            height=200
                        )
                        fig_ipc.update_traces(textposition='auto')
                        fig_ipc.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig_ipc, use_container_width=True)
                        st.write(f"**Efficient Products**: {insights['ipc_high_percent']:.1f}%")

                    with col4:
                        st.write("**Clicks per Conversion**")
                        cpc_data = pd.DataFrame({
                            'Category': ['High', 'Moderate', 'Low'],
                            'Count': [insights['cpc_high_count'], insights['cpc_moderate_count'], insights['cpc_low_count']],
                            'Percentage': [insights['cpc_high_percent'], insights['cpc_moderate_percent'], insights['cpc_low_percent']]
                        })
                        y_axis = 'Count' if view_option == "Count" else 'Percentage'
                        fig_cpc = px.bar(
                            cpc_data,
                            x=y_axis,
                            y='Category',
                            orientation='h',
                            color='Category',
                            color_discrete_map={'High': '#00CC96', 'Moderate': '#FFD700', 'Low': '#EF553B'},
                            text=cpc_data[y_axis].apply(lambda x: f"{x:.1f}{'%' if y_axis == 'Percentage' else ''}"),
                            height=200
                        )
                        fig_cpc.update_traces(textposition='auto')
                        fig_cpc.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig_cpc, use_container_width=True)
                        st.write(f"**Efficient Products**: {insights['cpc_high_percent']:.1f}%")

                    # Dynamic Recommendations
                    st.markdown("#### 💡 Recommendations")
                    if insights['ipc_low_percent'] > 50:
                        st.markdown("- 🚨 **High Low Performers in Impressions per Click**: Optimize ad creatives or refine audience targeting.")
                    else:
                        st.markdown("- ✅ **Impressions per Click**: Maintain current strategy; consider A/B testing new creatives.")
                    if insights['cpc_low_percent'] > 50:
                        st.markdown("- 🚨 **High Low Performers in Clicks per Conversion**: Audit landing pages for UX issues or offer adjustments.")
                    else:
                        st.markdown("- ✅ **Clicks per Conversion**: Keep optimizing; test call-to-action variations.")

                    # Note with Tooltip
                    st.markdown(
                        "<small>Note: <span title='High: Below average (efficient). Moderate: Near average. Low: Above average (inefficient).'>"
                        "Performance categories based on efficiency thresholds</span>.</small>",
                        unsafe_allow_html=True
                    )
                    st.divider()

                # Detected Columns Tab (unchanged)
                with tab2:
                    st.subheader("📂 Detected Columns")
                    st.write(df_processed.columns.tolist())

                # Debugging Tab (unchanged)
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
