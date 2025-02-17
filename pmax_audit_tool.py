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
        🔹 **Expected CSV Column Order:**
        | # | Column |
        |---|--------|
        | 1 | Item ID |
        | 2 | Impressions (Impr.) |
        | 3 | Clicks |
        | 4 | Click-Through Rate (CTR) |
        | 5 | Conversions |
        | 6 | Conversion Value (Conv. value) |
        | 7 | Conversion Value / Cost (Conv. value / cost) |
        | 8 | Search Impression Share |
        
        **Ensure that your CSV file follows this format before uploading.**
        """)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure column names are formatted correctly."""
    df.columns = (
        df.columns
        .str.strip()  # Remove leading/trailing spaces
        .str.lower()  # Convert to lowercase
        .str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with a single space
    )
    rename_map = {
        'item id': 'Item ID',
        'impr.': 'Impr.',
        'clicks': 'Clicks',
        'ctr': 'CTR',
        'conversions': 'Conversions',
        'conv. value': 'Conv. value',
        'conv. value / cost': 'Conv. value / cost',
        'search impr. share': 'Search impr. share'
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def assess_product_performance(df: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Assess product-level performance in Google PMAX campaigns."""
    df = clean_column_names(df)
    
    numeric_columns = ['Impr.', 'Clicks', 'Conversions', 'Conv. value', 'Conv. value / cost', 'Search impr. share']
    missing_columns = [col for col in ['Item ID'] + numeric_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ Missing columns in uploaded file: {', '.join(missing_columns)}")
        st.write("🔍 Detected Columns in Uploaded File:", df.columns.tolist())  # Debugging line
        return None, None  # Stop execution if critical columns are missing
    
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    df['Search impr. share'] = (
        df['Search impr. share']
        .astype(str)
        .str.replace("%", "", regex=True)
        .replace("--", "0")
        .apply(lambda x: pd.to_numeric(x, errors='coerce') / 100 if x != '' else 0)
        .fillna(0)
    )
    
    total_item_count = df.shape[0]
    df_sorted = df.sort_values(by='Conversions', ascending=False)
    df_sorted['Cumulative_Conversions'] = df_sorted['Conversions'].cumsum()
    df_sorted['Cumulative_Conversions_Percentage'] = (df_sorted['Cumulative_Conversions'] / df_sorted['Conversions'].sum()) * 100
    num_products_80 = df_sorted[df_sorted['Cumulative_Conversions_Percentage'] >= 80].shape[0]
    
    impressions_sum = df['Impr.'].sum()
    average_ctr = round(df['Clicks'].sum() / impressions_sum * 100, 2) if impressions_sum else 0
    
    insights = {
        'total_item_count': total_item_count,
        'total_impressions': int(df['Impr.'].sum()),
        'total_clicks': int(df['Clicks'].sum()),
        'average_ctr': average_ctr,
        'total_conversions': int(df['Conversions'].sum()),
        'total_conversion_value': round(df['Conv. value'].sum(), 2),
        'average_roas': round(df['Conv. value / cost'].mean(), 2),
        'num_products_80': num_products_80,
        'percent_skus_driving_80': round((num_products_80 / total_item_count) * 100, 2) if total_item_count > 0 else 0,
        'average_search_impr_share': round(df['Search impr. share'].mean(skipna=True) * 100, 2)
    }
    
    return insights, df

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file."""
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaign data.")
    print_expected_csv_format()
    
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    
    if uploaded_file:
        with st.spinner("Processing file..."):
            df = pd.read_csv(uploaded_file, skiprows=2)  # Skip first two rows to handle incorrect structure
            insights, df_processed = assess_product_performance(df)
            
            if insights:
                st.write("📂 Preview of Uploaded Data:")
                st.dataframe(df_processed.head())
                
                st.download_button(
                    label="📥 Download Processed Data",
                    data=df_processed.to_csv(index=False).encode('utf-8'),
                    file_name="processed_data.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    run_web_ui()
