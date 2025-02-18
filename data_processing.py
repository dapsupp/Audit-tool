import pandas as pd 
import difflib
import logging
from thefuzz import process

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data:
    - Cleans & maps column names dynamically
    - Ensures all columns exist
    - Converts numeric fields safely
    - Provides business insights
    """
    df = clean_column_names(df)
    missing_columns = validate_columns(df)

    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns} (Check CSV Formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    # Convert numeric values safely (handle cases where they are stored as strings)
    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'conversion_value_cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)  # Convert to float, replace errors with 0

    # Convert CTR percentages into decimal format
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': float(df['impressions'].sum()),
        'total_clicks': float(df['clicks'].sum()),
        'average_ctr': float(df['ctr'].mean() * 100 if 'ctr' in df.columns else 0),
        'total_conversions': float(df['conversions'].sum()),
        'total_conversion_value': float(df['conversion_value'].sum() if 'conversion_value' in df.columns else 0),
    }

    logging.info("✅ Successfully processed data insights")
    return insights, df
