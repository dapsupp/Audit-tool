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
    df.columns = df.columns.str.strip().str.lower().replace(' ', '_')
    rename_map = {
        'item_id': 'item id',
        'impressions': 'impr.',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'conversions': 'conversions',
        'conversion_value': 'conv. value',
        'conversion_value_/cost': 'conv. value / cost',
        'search_impression_share': 'search impr. share'
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def assess_product_performance(df: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Assess product-level performance in Google PMAX campaigns."""
    df = clean_column_names(df)
    
    numeric_columns = ['impr.', 'clicks', 'conversions', 'conv. value', 'conv. value / cost', 'search impr. share']
    missing_columns = [col for col in ['item id'] + numeric_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ Missing columns in uploaded file: {', '.join(missing_columns)}")
        return None, None  # Stop execution if critical columns are missing
    
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    df['search impr. share'] = (
        df['search impr. share']
        .astype(str)
        .str.replace("%", "", regex=True)
        .replace("--", "0")
        .apply(lambda x: pd.to_numeric(x, errors='coerce') / 100 if x != '' else 0)
        .fillna(0)
    )
    
    total_item_count = df.shape[0]
    df_sorted = df.sort_values(by='conversions', ascending=False)
    df_sorted['cumulative_conversions'] = df_sorted['conversions'].cumsum()
    df_sorted['cumulative_conversions_percentage'] = (df_sorted['cumulative_conversions'] / df_sorted['conversions'].sum()) * 100
    num_products_80 = df_sorted[df_sorted['cumulative_conversions_percentage'] >= 80].shape[0]
    
    impressions_sum = df['impr.'].sum()
    average_ctr = round(df['clicks'].sum() / impressions_sum * 100, 2) if impressions_sum else 0
    
    insights = {
        'total_item_count': total_item_count,
        'total_impressions': int(df['impr.'].sum()),
        'total_clicks': int(df['clicks'].sum()),
        'average_ctr': average_ctr,
        'total_conversions': int(df['conversions'].sum()),
        'total_conversion_value': round(df['conv. value'].sum(), 2),
        'average_roas': round(df['conv. value / cost'].mean(), 2),
        'num_products_80': num_products_80,
        'percent_skus_driving_80': round((num_products_80 / total_item_count) * 100, 2) if total_item_count > 0 else 0,
        'average_search_impr_share': round(df['search impr. share'].mean(skipna=True) * 100, 2)
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
                create_summary_table(insights)
            
                st.download_button(
                    label="📥 Download Processed Data",
                    data=df_processed.to_csv(index=False).encode('utf-8'),
                    file_name="processed_data.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    run_web_ui()
