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
                    # ✅ **Modern KPI Cards (Now with Proper Spacing)**
                    st.subheader("📊 Key Metrics Overview")

                    col1, col2, col3 = st.columns(3)

                    # Improved Card Styling with Spacing
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
                            margin: 10px;  /* ✅ Adds spacing between cards */
                        ">
                            <h3 style="color: white;">{}</h3>
                            <p style="font-size: 30px; margin: 5px 0;">{}</p>
                        </div>
                    """

                    with col1:
                        st.markdown(card_style.format("🛍️ Total Items", f"{insights['total_item_count']:,}"), unsafe_allow_html=True)
                        st.markdown(card_style.format("📈 Total Impressions", f"{insights['total_impressions']:,}"), unsafe_allow_html=True)

                    with col2:
                        st.markdown(card_style.format("📊 Average CTR", f"{insights['average_ctr']:.2f}%"), unsafe_allow_html=True)
                        st.markdown(card_style.format("💰 Total Conversion Value", f"£{insights['total_conversion_value']:.2f}"), unsafe_allow_html=True)

                    with col3:
                        st.markdown(card_style.format("🔍 Search Impression Share", f"{insights['average_search_impression_share']:.2f}%"), unsafe_allow_html=True)
                        st.markdown(card_style.format("⚡ ROAS (Return on Ad Spend)", f"{insights['roas']:.2f}"), unsafe_allow_html=True)

                # ✅ **Everything Else Remains the Same**

            except KeyError as e:
                logging.error(f"❌ Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
