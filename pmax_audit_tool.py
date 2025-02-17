import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from typing import Tuple, Dict

# Ensure table rendering works correctly
pio.renderers.default = "browser"

def print_expected_csv_format():
    """Displays the expected CSV format for the user."""
    st.markdown(
        """
        ## 🔹 Expected CSV Column Order
        | # | Column |
        |---|------------------------------|
        | 1 | Item ID |
        | 2 | Impressions (Impr.) |
        | 3 | Clicks |
        | 4 | Click-Through Rate (CTR) |
        | 5 | Conversions |
        | 6 | Conversion Value (Conv. value) |
        | 7 | Cost |
        | 8 | Conversion Value / Cost (ROAS) |
        | 9 | Search Impression Share |
        
        **Ensure that your CSV file follows this format before uploading.**
        """)

def detect_header_row(file_path: str) -> int:
    """Detects the correct header row by scanning the first few lines of the CSV."""
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "Item ID" in line and "Impr." in line:
                return i  # This row is the actual header
    return 0  # Default to first row if no match is found

def process_large_csv(file_path: str, chunk_size: int = 100000) -> Dict[str, float]:
    """Processes large CSV files in chunks, automatically detecting the header row."""
    
    # Detect correct header row
    header_row = detect_header_row(file_path)
    
    # Initialize totals
    total_impressions = 0
    total_clicks = 0
    total_conversions = 0
    total_conversion_value = 0
    total_cost = 0
    total_search_impr_share = 0
    valid_search_impr_count = 0
    
    try:
        for chunk in pd.read_csv(
            file_path, 
            chunksize=chunk_size, 
            encoding="utf-8", 
            on_bad_lines="skip", 
            skiprows=header_row
        ):
            # Normalize column names
            chunk.columns = chunk.columns.str.strip().str.lower()
            
            # Verify if required columns exist
            required_columns = ["impr.", "clicks", "conversions", "conv. value", "cost"]
            missing_columns = [col for col in required_columns if col not in chunk.columns]
            if missing_columns:
                st.error(f"❌ Missing expected columns: {', '.join(missing_columns)}")
                st.write("🔍 Detected Columns in Uploaded File:", list(chunk.columns))
                return {}
            
            # Clean and convert numeric columns
            for col in required_columns:
                chunk[col] = chunk[col].astype(str).str.replace(",", "").astype(float)
            
            # Calculate ROAS dynamically if missing
            chunk["roas"] = chunk.apply(lambda row: row["conv. value"] / row["cost"] if row["cost"] > 0 else 0, axis=1)
            
            # Process Search Impression Share
            chunk["search impr. share"] = (
                chunk["search impr. share"]
                .astype(str)
                .str.replace("%", "")
                .replace("--", "")
                .apply(pd.to_numeric, errors='coerce')
            )
            
            # Aggregate Metrics
            total_impressions += chunk["impr."].sum()
            total_clicks += chunk["clicks"].sum()
            total_conversions += chunk["conversions"].sum()
            total_conversion_value += chunk["conv. value"].sum()
            total_cost += chunk["cost"].sum()
            
            valid_search_chunk = chunk["search impr. share"].dropna()
            total_search_impr_share += valid_search_chunk.sum()
            valid_search_impr_count += len(valid_search_chunk)
        
        # Compute Final Metrics
        average_roas = total_conversion_value / total_cost if total_cost > 0 else 0
        average_search_impr_share = (total_search_impr_share / valid_search_impr_count) if valid_search_impr_count > 0 else 0
        
        return {
            "Total Impressions": total_impressions,
            "Total Clicks": total_clicks,
            "Total Conversions": total_conversions,
            "Total Conversion Value": total_conversion_value,
            "Total Cost": total_cost,
            "Average ROAS": round(average_roas, 2),
            "Average Search Impression Share": round(average_search_impr_share, 2)
        }
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return {}

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file and processing it in chunks."""
    st.title("📊 PMax Audit Dashboard")
    st.write("Analyze your Performance Max campaign data efficiently without file size limits.")
    print_expected_csv_format()
    
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader")
    
    if uploaded_file:
        with st.spinner("Processing file..."):
            # Save uploaded file to a temporary location
            file_path = "uploaded_data.csv"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the file in chunks
            insights = process_large_csv(file_path)
            
            if insights:
                st.subheader("📊 Summary Metrics")
                summary_df = pd.DataFrame({"Metric": insights.keys(), "Value": insights.values()})
                st.table(summary_df)

if __name__ == "__main__":
    st.cache_data.clear()  # Clear cache to prevent duplicate elements
    run_web_ui()
