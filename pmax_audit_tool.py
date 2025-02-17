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

def process_large_csv(file_path: str, chunk_size: int = 100000) -> Dict[str, float]:
    """Processes large CSV files in chunks to avoid memory constraints."""
    
    # Initialize totals
    total_impressions = 0
    total_clicks = 0
    total_conversions = 0
    total_conversion_value = 0
    total_cost = 0
    total_search_impr_share = 0
    valid_search_impr_count = 0
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Clean and convert numeric columns
        chunk["Impr."] = chunk["Impr."].astype(str).str.replace(",", "").astype(float)
        chunk["Clicks"] = chunk["Clicks"].astype(str).str.replace(",", "").astype(float)
        chunk["Conversions"] = chunk["Conversions"].astype(str).str.replace(",", "").astype(float)
        chunk["Conv. value"] = chunk["Conv. value"].astype(str).str.replace(",", "").astype(float)
        chunk["Cost"] = chunk["Cost"].astype(str).str.replace(",", "").astype(float)
        
        # Calculate ROAS dynamically if missing
        chunk["ROAS"] = chunk.apply(lambda row: row["Conv. value"] / row["Cost"] if row["Cost"] > 0 else 0, axis=1)
        
        # Process Search Impression Share
        chunk["Search impr. share"] = (
            chunk["Search impr. share"]
            .astype(str)
            .str.replace("%", "")
            .replace("--", "")
            .apply(pd.to_numeric, errors='coerce')
        )
        
        # Aggregate Metrics
        total_impressions += chunk["Impr."].sum()
        total_clicks += chunk["Clicks"].sum()
        total_conversions += chunk["Conversions"].sum()
        total_conversion_value += chunk["Conv. value"].sum()
        total_cost += chunk["Cost"].sum()
        
        valid_search_chunk = chunk["Search impr. share"].dropna()
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

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file and processing it in chunks."""
    st.title("📊 PMax Audit Dashboard - Scalable Version")
    st.write("Analyze your Performance Max campaign data efficiently without file size limits.")
    print_expected_csv_format()
    
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")
    
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
    run_web_ui()
