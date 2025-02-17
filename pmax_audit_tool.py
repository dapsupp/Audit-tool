import streamlit as st
import pandas as pd
from data_processing import assess_product_performance

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file."""
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaigns.")

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader_1")

    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                df = pd.read_csv(uploaded_file, delimiter=",", skiprows=2, error_bad_lines=False)
                insights, df_processed = assess_product_performance(df)

                if insights:
                    st.subheader("📊 Summary Metrics")
                    st.write(insights)
                    st.write("📂 Preview of Processed Data:")
                    st.dataframe(df_processed.head())

                    st.download_button(
                        label="📥 Download Processed Data",
                        data=df_processed.to_csv(index=False).encode('utf-8'),
                        file_name="processed_data.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    run_web_ui()
