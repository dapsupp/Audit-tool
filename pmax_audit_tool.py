import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import tempfile
import logging
from typing import Dict

# Configure logging to file for error tracking
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Ensure that table rendering works correctly
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
        """
    )

def detect_header_row(file_path: str) -> int:
    """Detects the correct header row by scanning the first few lines of the CSV."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if "Item ID" in line and "Impr." in line:
                    return i  # This row is the actual header
    except Exception as e:
        logging.error(f"Error detecting header row: {e}")
    return 0  # Default to first row if no match is found

def process_large_csv(file_path: str, chunk_size: int = 100000) -> Dict[str, float]:
    """Processes large CSV files in chunks, automatically detecting the header row."""
    
    # Detect the correct header row
    header_row = detect_header_row(file_path)
    
    # Initialise totals
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
            # Normalise column names
            chunk.columns = chunk.columns.str.strip().str.lower()
            
            # Verify if required columns exist
            required_columns = ["impr.", "clicks", "conversions", "conv. value", "cost"]
            missing_columns = [col for col in required_columns if col not in chunk.columns]
            if missing_columns:
                st.error(f"❌ Missing expected columns: {', '.join(missing_columns)}")
                st.write("🔍 Detected Columns in Uploaded File:", list(chunk.columns))
                return {}
            
            # Clean and convert numeric columns in a vectorised manner
            for col in required_columns:
                chunk[col] = pd.to_numeric(chunk[col].astype(str).str.replace(",", ""), errors='coerce').fillna(0)
            
            # Calculate ROAS using vectorised operations
            chunk["roas"] = chunk["conv. value"] / chunk["cost"]
            chunk.loc[chunk["cost"] <= 0, "roas"] = 0
            
            # Process Search Impression Share if present
            if "search impr. share" in chunk.columns:
                chunk["search impr. share"] = pd.to_numeric(
                    chunk["search impr. share"].astype(str).str.replace("%", "").replace("--", ""),
                    errors='coerce'
                )
            else:
                chunk["search impr. share"] = pd.NA
            
            # Aggregate Metrics
            total_impressions += chunk["impr."].sum()
            total_clicks += chunk["clicks"].sum()
            total_conversions += chunk["conversions"].sum()
            total_conversion_value += chunk["conv. value"].sum()
            total_cost += chunk["cost"].sum()
            
            valid_search_chunk = chunk["search impr. share"].dropna()
            total_search_impr_share += valid_search_chunk.sum()
            valid_search_impr_count += valid_search_chunk.count()
        
        # Compute final metrics
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
        logging.error(f"Error processing CSV file: {e}")
        return {}

def create_metrics_bar_chart(insights: Dict[str, float]) -> go.Figure:
    """Creates a Plotly bar chart for the summary metrics."""
    # Visualise total metrics only for the bar chart
    metrics = {
        "Total Impressions": insights.get("Total Impressions", 0),
        "Total Clicks": insights.get("Total Clicks", 0),
        "Total Conversions": insights.get("Total Conversions", 0),
        "Total Conversion Value": insights.get("Total Conversion Value", 0),
        "Total Cost": insights.get("Total Cost", 0)
    }
    
    fig = go.Figure(data=[go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color='indianred'
    )])
    
    fig.update_layout(
        title="Campaign Performance Metrics",
        xaxis_title="Metric",
        yaxis_title="Value",
        template="plotly_white"
    )
    
    return fig

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file and processing it in chunks."""
    st.title("📊 PMax Audit Dashboard")
    st.write("Analyse your Performance Max campaign data efficiently without file size limits.")
    print_expected_csv_format()
    
    uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader")
    
    if uploaded_file:
        with st.spinner("Processing file..."):
            try:
                # Use a temporary file for handling the uploaded CSV
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name
                
                # Process the file in chunks
                insights = process_large_csv(tmp_file_path)
                
                if insights:
                    st.subheader("📊 Summary Metrics")
                    summary_df = pd.DataFrame({
                        "Metric": list(insights.keys()),
                        "Value": list(insights.values())
                    })
                    st.table(summary_df)
                    
                    # Display an interactive bar chart using Plotly
                    st.subheader("📈 Visual Overview")
                    fig = create_metrics_bar_chart(insights)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.error(f"Unexpected error in run_web_ui: {e}")

if __name__ == "__main__":
    # Clear cache to prevent duplicate elements
    st.cache_data.clear()  
    run_web_ui()
