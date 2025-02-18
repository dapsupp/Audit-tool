import pandas as pd
import difflib
import logging

# Configure logging
logging.basicConfig(
    filename="data_processing.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

EXPECTED_COLUMNS = {
    'item_id': 'item_id',
    'impressions': 'impr.',
    'clicks': 'clicks',
    'ctr': 'ctr',
    'conversions': 'conversions',
    'conversion_value': 'conv_value',
    'conv. value': 'conv_value',  
    'conversion value': 'conv_value',
    'conversion_value_/_cost': 'conv_value_cost',
    'conversion value / cost': 'conv_value_cost',
    'search impression share': 'search_impr_share',
    'search_impression_share': 'search_impr_share',
    'search impr. share': 'search_impr_share'
}

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """ Cleans column names dynamically using fuzzy matching. """
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    renamed_columns = {}
    for col in df.columns:
        closest_match = difflib.get_close_matches(col, EXPECTED_COLUMNS.keys(), n=1, cutoff=0.7)
        if closest_match:
            new_name = EXPECTED_COLUMNS[closest_match[0]]
            renamed_columns[col] = new_name
        else:
            renamed_columns[col] = col  

    df.rename(columns=renamed_columns, inplace=True)
    logging.info(f"✅ Column Mapping Applied: {renamed_columns}")

    return df

def validate_columns(df: pd.DataFrame) -> list:
    """ Ensures all required columns exist. """
    required_columns = list(set(EXPECTED_COLUMNS.values()))
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns

def assess_product_performance(df: pd.DataFrame):
    """ Processes Google PMAX campaign data and provides insights. """
    df = clean_column_names(df)
    missing_columns = validate_columns(df)

    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns}"
        logging.error(error_message)
        raise KeyError(error_message)

    numeric_cols = ['impr.', 'clicks', 'conversions', 'conv_value', 'conv_value_cost']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': df['impr.'].sum(),
        'total_clicks': df['clicks'].sum(),
        'average_ctr': df['ctr'].mean() * 100 if 'ctr' in df.columns else 0,
        'total_conversions': df['conversions'].sum(),
        'total_conversion_value': df['conv_value'].sum() if 'conv_value' in df.columns else 0,
    }

    logging.info("✅ Successfully processed data insights")
    return insights, df  # ✅ No extra closing brace here!
