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
                    # ✅ **Modern KPI Cards**
                    st.subheader("📊 Key Metrics Overview")
                    
                    col1, col2, col3 = st.columns(3)

                    # Styled KPI Cards
                    with col1:
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>🛍️ Total Items</h3>
                                <p style="font-size: 24px; font-weight: bold;">{insights['total_item_count']:,}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>📈 Total Impressions</h3>
                                <p style="font-size: 24px; font-weight: bold;">{insights['total_impressions']:,}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col2:
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>📊 Average CTR</h3>
                                <p style="font-size: 24px; font-weight: bold;">{insights['average_ctr']:.2f}%</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>💰 Total Conversion Value</h3>
                                <p style="font-size: 24px; font-weight: bold;">£{insights['total_conversion_value']:.2f}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col3:
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>🔍 Search Impression Share</h3>
                                <p style="font-size: 24px; font-weight: bold;">{insights['average_search_impression_share']:.2f}%</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3>⚡ ROAS (Return on Ad Spend)</h3>
                                <p style="font-size: 24px; font-weight: bold;">{insights['roas']:.2f}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # ✅ **Pareto Law Insights - Styled Table**
                    st.subheader("📈 Pareto Law: SKU Contribution Breakdown")
                    st.dataframe(sku_table, height=300)

                    # ✅ **Graph Section - Max Width & Centered**
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
                        width=700,  # ✅ Fixed Width
                        height=300  # ✅ Properly Sized
                    )

                    fig.update_traces(texttemplate='%{text}%', textposition='outside')

                    st.plotly_chart(fig, use_container_width=False)
                    st.markdown("</div>", unsafe_allow_html=True)

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
