import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import assess_product_performance
import logging

# Configure logging
logging.basicConfig(filename="pmax_audit_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Custom styling for tables
def style_dataframe(df):
    """
    Applies styling to the dataframe for a better UI.
    - Highlights high ROAS in green
    - Highlights low conversions in red
    - Formats currency fields properly
    """
    def highlight_values(val):
        """Color coding for better readability."""
        if isinstance(val, (int, float)):
            if val > 50000:
                return 'background-color: #A7FFEB; color: black;'  # Green for high values
            elif val < 1000:
                return 'background-color: #FF8A80; color: black;'  # Red for low values
        return ""

    return df.style.format({
        "total_conversion_value": "£{:.2f}",
        "average_ctr": "{:.2f}%",
        "average_roas": "{:.2f}"
    }).applymap(highlight_values)

def run_web_ui():
    """Creates a modern web-based interface for PMax Audit Tool."""
    st.set_page_config(page_title="📊 PMax Audit Tool", layout="wide")

    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                # Try multiple encodings if needed
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1", on_bad_lines="skip")

                logging.info(f"📂 Detected Columns: {df.columns.tolist()}")

                insights, df_processed = assess_product_performance(df)

                if insights:
                    st.subheader("📊 Summary Metrics")
                    summary_df = pd.DataFrame([insights])
                    
                    # Modern styled table
                    st.dataframe(
                        summary_df.style.format({
                            "total_conversion_value": "£{:.2f}",
                            "average_ctr": "{:.2f}%",
                            "average_roas": "{:.2f}"
                        })
                        .set_properties(**{"background-color": "#f9f9f9", "color": "black", "border-color": "black"})
                    )

                    # Display product-level data with improved UI
                    st.subheader("📂 Processed Data Preview")
                    st.dataframe(style_dataframe(df_processed), height=600)

                    st.download_button(
                        label="📥 Download Processed Data",
                        data=df_processed.to_csv(index=False).encode('utf-8'),
                        file_name="processed_data.csv",
                        mime="text/csv"
                    )
            except KeyError as e:
                logging.error(f"Missing columns: {e}")
                st.error(f"⚠️ Missing columns: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_web_ui()
