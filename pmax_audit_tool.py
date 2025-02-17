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

def process_search_impr_share(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and processes the Search Impression Share column."""
    if 'Search impr. share' in df.columns:
        df['Search impr. share'] = (
            df['Search impr. share']
            .astype(str)
            .str.replace("%", "", regex=True)
            .str.strip()
            .replace("--", "0")
            .apply(lambda x: pd.to_numeric(x, errors='coerce'))
            .fillna(0)
        ) / 100
    print("Processed Search Impression Share Values:")
    print(df[['Item ID', 'Search impr. share']].head())  # Debugging print
    return df

def assess_product_performance(df: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Assess product-level performance in Google PMAX campaigns."""
    df = clean_column_names(df)
    df = process_search_impr_share(df)
    
    numeric_columns = ['Impr.', 'Clicks', 'Conversions', 'Conv. value', 'Conv. value / cost', 'Search impr. share']
    missing_columns = [col for col in ['Item ID'] + numeric_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ Missing columns in uploaded file: {', '.join(missing_columns)}")
        st.write("🔍 Detected Columns in Uploaded File:", df.columns.tolist())
        return None, None
    
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    total_item_count = df.shape[0]
    df_sorted = df.sort_values(by='Conversions', ascending=False)
    df_sorted['Cumulative_Conversions'] = df_sorted['Conversions'].cumsum()
    df_sorted['Cumulative_Conversions_Percentage'] = (df_sorted['Cumulative_Conversions'] / df_sorted['Conversions'].sum()) * 100
    num_products_80 = df_sorted[df_sorted['Cumulative_Conversions_Percentage'] >= 80].shape[0]
    
    impressions_sum = df['Impr.'].sum()
    average_ctr = round(df['Clicks'].sum() / impressions_sum * 100, 2) if impressions_sum else 0
    
    search_impr_share_values = df['Search impr. share'].dropna()
    actual_avg_search_impr_share = round(search_impr_share_values.mean() * 100, 2)
    print(f"Debug - Expected Average Search Impression Share: {actual_avg_search_impr_share}%")
    
    insights = {
        'Total SKUs': total_item_count,
        'Total Impressions': int(df['Impr.'].sum()),
        'Total Clicks': int(df['Clicks'].sum()),
        'Average CTR': f"{average_ctr:.2f}%",
        'Total Conversions': int(df['Conversions'].sum()),
        'Total Conversion Value': f"£{df['Conv. value'].sum():,.2f}",
        'Average ROAS': round(df['Conv. value / cost'].mean(), 2),
        'SKUs Driving 80% of Sales': num_products_80,
        'Percentage of SKUs Driving 80% of Sales': f"{round((num_products_80 / total_item_count) * 100, 2)}%" if total_item_count > 0 else "0%",
        'Average Search Impression Share': f"{actual_avg_search_impr_share}%"
    }
    
    return insights, df
