import pandas as pd
import difflib
import logging

# Configure logging
logging.basicConfig(filename="data_processing.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Expected column names mapping
EXPECTED_COLUMNS = {
    'item_id': 'item_id',
    'impressions': 'impr.',
    'clicks': 'clicks',
    'ctr': 'ctr',
    'conversions': 'conversions',
    'conversion_value': 'conv_value',
    'conversion value': 'conv_value',
    'conv. value': 'conv_value',
    'conversion_value_/_cost': 'conv_value_cost',
    'conversion value / cost': 'conv_value_cost',
    'search impression share': 'search_impr_share',
    'search_impression_share': 'search_impr_share',  # Ensure all variations are covered
    'search impr. share': 'search_impr_share'
}

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes column names:
    - Converts to lowercase
    - Strips spaces & replaces with underscores
    - Matches columns dynamically using fuzzy matching
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    # Find closest matches for existing columns
    renamed_columns = {}
    for col in df.columns:
        closest_match = difflib.get_close_matches(col, EXPECTED_COLUMNS.keys(), n=1, cutoff=0.7)
        if closest_match:
            new_name = EXPECTED_COLUMNS[closest_match[0]]
            renamed_columns[col] = new_name
        else:
            renamed_columns[col] = col  # Keep it unchanged if no match

    df.rename(columns=renamed_columns, inplace=True)
    logging.info(f"Column mapping applied: {renamed_columns}")

    return df

def validate_columns(df: pd.DataFrame) -> list:
    """
    Checks for missing columns and returns a list of required but absent columns.
    """
    required_columns = list(EXPECTED_COLUMNS.values())
    missing_columns = [col for col in required_columns if col not in df.columns]

    return missing_columns

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data:
    - Cleans & maps column names dynamically
    - Converts numeric fields safely
    - Provides summary insights
    """
    df = clean_column_names(df)
    missing_columns = validate_columns(df)

    if missing_columns:
        error_message = f"🚨 Missing required columns: {missing_columns} (Check CSV formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    # Convert numeric values safely
    for col in ['impr.', 'clicks', 'conversions', 'conv_value']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert CTR percentages into decimal format
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': df['impr.'].sum(),
        'total_clicks': df['clicks'].sum(),
        'average_ctr': df['ctr'].mean() * 100 if 'ctr' in df.columns else 0,
        'total_conversions': df['conversions'].sum(),
        'total_conversion_value': df['conv_value'].sum(),
    }

    logging.info("Successfully processed data insights")
    return insights, df
