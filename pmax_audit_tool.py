import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from typing import Tuple, Dict

# Ensure table rendering works correctly
pio.renderers.default = "browser"

# Expected CSV Column Order Reminder
def print_expected_csv_format():
    """Prints the expected CSV format to remind the user of the required field order."""
    st.info("🔹 Expected CSV Column Order:\n\n"
            "1. Item ID\n"
            "2. Impressions (Impr.)\n"
            "3. Clicks\n"
            "4. Click-Through Rate (CTR)\n"
            "5. Conversions\n"
            "6. Conversion Value (Conv. value)\n"
            "7. Conversion Value / Cost (Conv. value / cost)\n\n"
            "Please ensure that your CSV file follows this format before uploading.")

def clean_column_names(df):
    """Ensure column names are formatted correctly."""
    df.columns = df.columns.str.strip().str.lower()
    rename_map = {
        'item id': 'item id',
        'impressions': 'impr.',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'conversions': 'conversions',
        'conversion value': 'conv. value',
        'conversion value / cost': 'conv. value / cost'
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def assess_product_performance(df: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Assess product-level performance in Google PMAX campaigns."""
    df = clean_column_names(df)
    
    numeric_columns = ['impr.', 'clicks', 'conversions', 'conv. value', 'conv. value / cost']
    missing_columns = [col for col in ['item id'] + numeric_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Missing columns in uploaded file: {missing_columns}")
        return {}, df
    
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    total_item_count = df.shape[0]
    df_sorted = df.sort_values(by='conversions', ascending=False)
    df_sorted['cumulative_conversions'] = df_sorted['conversions'].cumsum()
    df_sorted['cumulative_conversions_percentage'] = (df_sorted['cumulative_conversions'] / df_sorted['conversions'].sum()) * 100
    num_products_80 = (df_sorted['cumulative_conversions_percentage'] >= 80).idxmax() + 1
    
    percent_skus_driving_80 = round((num_products_80 / total_item_count) * 100, 2) if total_item_count > 0 else 0
    
    insights = {
        'total_item_count': total_item_count,
        'total_impressions': int(df['impr.'].sum()),
        'total_clicks': int(df['clicks'].sum()),
        'average_ctr': round((df['clicks'].sum() / df['impr.'].sum() * 100) if df['impr.'].sum() > 0 else 0, 2),
        'total_conversions': int(df['conversions'].sum()),
        'total_conversion_value': round(df['conv. value'].sum(), 2),
        'average_roas': round(df['conv. value / cost'].mean(), 2),
        'num_products_80': num_products_80,
        'percent_skus_driving_80': percent_skus_driving_80
    }
    
    return insights, df

def create_summary_table(insights: Dict[str, float]) -> None:
    """Create a summary table with key insights."""
    summary_df = pd.DataFrame({
        "Metric": [
            "Total Number of SKUs", "Total Impressions", "Total Clicks", "Average Click-Through Rate (CTR)", "Total Conversions", 
            "Total Conversion Value (£)", "Average Return on Ad Spend (ROAS)", "Number of SKUs Driving 80% of Sales", "Percentage of SKUs Driving 80% of Sales"
        ],
        "Value": [
            f"{insights['total_item_count']:,}",
            f"{insights['total_impressions']:,}",
            f"{insights['total_clicks']:,}",
            f"{insights['average_ctr']:.2f}%",
            f"{insights['total_conversions']:,}",
            f"£{insights['total_conversion_value']:,.2f}",
            f"{insights['average_roas']:.2f}",
            f"{insights['num_products_80']:,}",
            f"{insights['percent_skus_driving_80']:.2f}%"
        ]
    })
    st.table(summary_df)

def run_web_ui():
    """Creates a web-based interface for uploading a CSV file."""
    st.title("📊 PMax Audit Tool")
    st.write("Upload your CSV file below to analyze Performance Max campaign data.")
    print_expected_csv_format()
    
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        insights, _ = assess_product_performance(df)
        create_summary_table(insights)

if __name__ == "__main__":
    run_web_ui()
