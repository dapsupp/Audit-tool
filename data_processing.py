import pandas as pd
import difflib
import logging

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame's column names by:
    - Stripping whitespace
    - Converting to lowercase
    - Replacing spaces and dots with underscores
    - Mapping common abbreviations to expected names
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('.', '_')
    )
    
    rename_mapping = {
        'impr_': 'impressions',
        'conv__value': 'conversion_value',
        'conv__value_/_cost': 'conversion_value_cost',
        'search_impr__share': 'search_impression_share',
        'cost': 'cost'
    }
    
    df.rename(columns=rename_mapping, inplace=True)
    
    return df

def validate_columns(df: pd.DataFrame) -> list:
    """
    Validates that the required columns exist in the DataFrame.
    If any required columns are missing, returns a list of them.
    """
    required_columns = ['impressions', 'clicks', 'ctr', 'conversions', 'conversion_value', 'conversion_value_cost', 'search_impression_share', 'cost']
    
    missing = []
    for col in required_columns:
        if col not in df.columns:
            close_matches = difflib.get_close_matches(col, df.columns)
            if close_matches:
                logging.warning(f"Column '{col}' not found, but found close match: {close_matches[0]}. Consider renaming.")
            else:
                missing.append(col)
    return missing

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data:
    - Cleans & maps column names dynamically
    - Ensures all required columns exist
    - Converts numeric fields safely, handling comma-separated values
    - Provides business insights
    """
    df = clean_column_names(df)
    
    missing_columns = validate_columns(df)
    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns} (Check CSV Formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'conversion_value_cost', 'search_impression_share', 'cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)

    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100
    
    total_conversion_value = float(df['conversion_value'].sum() if 'conversion_value' in df.columns else 0)
    total_cost = float(df['cost'].sum() if 'cost' in df.columns else 0)
    roas = (total_conversion_value / total_cost) if total_cost > 0 else 0

    avg_search_impression_share = df['search_impression_share'].mean() * 100 if 'search_impression_share' in df.columns and df['search_impression_share'].sum() > 0 else 0

    # Pareto Law Analysis (80% of sales driven by how many SKUs)
    top_skus_count = 0  # Ensure this variable is always defined
    top_skus_percentage = 0  # Default to zero if calculation fails

    if total_conversion_value > 0 and 'conversion_value' in df.columns:
        df_sorted = df.sort_values(by='conversion_value', ascending=False)
        df_sorted['cumulative_sum'] = df_sorted['conversion_value'].cumsum()
        threshold = total_conversion_value * 0.8
        top_skus = df_sorted[df_sorted['cumulative_sum'] <= threshold]

        top_skus_count = top_skus.shape[0]
        top_skus_percentage = (top_skus_count / df.shape[0]) * 100 if df.shape[0] > 0 else 0

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': float(df['impressions'].sum()),
        'total_clicks': float(df['clicks'].sum()),
        'average_ctr': float(df['ctr'].mean() * 100 if 'ctr' in df.columns else 0),
        'total_conversions': float(df['conversions'].sum()),
        'total_conversion_value': total_conversion_value,
        'total_cost': total_cost,
        'average_search_impression_share': avg_search_impression_share,
        'roas': roas,
        'top_skus_count': top_skus_count,  # ✅ Ensuring this key is always in the insights dictionary
        'top_skus_percentage': top_skus_percentage,
    }

    logging.info("✅ Successfully processed data insights")
    return insights, df
