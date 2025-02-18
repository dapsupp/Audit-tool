import pandas as pd
import difflib
import logging
from thefuzz import process

# Configure logging
logging.basicConfig(
    filename="data_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define the expected schema
EXPECTED_SCHEMA = {
    'item_id': 'int64',
    'impressions': 'int64',
    'clicks': 'int64',
    'ctr': 'float64',
    'conversions': 'int64',
    'conversion_value': 'float64',
    'conversion_value_cost': 'float64',
    'search_impr_share': 'float64'
}

# Standardized expected column mappings
EXPECTED_COLUMNS = {
    'item_id': 'item_id',
    'impressions': 'impressions',
    'clicks': 'clicks',
    'ctr': 'ctr',
    'conversions': 'conversions',
    'conv. value': 'conversion_value',
    'conversion value': 'conversion_value',
    'conversion_value/cost': 'conversion_value_cost',
    'conversion value / cost': 'conversion_value_cost',
    'search impression share': 'search_impr_share',
    'search_impression_share': 'search_impr_share',
    'search impr. share': 'search_impr_share'
}

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-corrects column names using fuzzy matching.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    renamed_columns = {}
    for col in df.columns:
        match, score = process.extractOne(col, EXPECTED_COLUMNS.keys(), score_cutoff=75)
        if match:
            renamed_columns[col] = EXPECTED_COLUMNS[match]
        else:
            renamed_columns[col] = col  # Keep unchanged if no close match found

    df.rename(columns=renamed_columns, inplace=True)
    logging.info(f"✅ Column Mapping Applied: {renamed_columns}")

    return df

def validate_columns(df: pd.DataFrame) -> list:
    """
    Ensures all required columns exist post-cleaning.
    """
    required_columns = list(EXPECTED_SCHEMA.keys())
    missing_columns = [col for col in required_columns if col not in df.columns]

    return missing_columns

def validate_data_types(df: pd.DataFrame):
    """
    Ensures that all columns match their expected data types.
    """
    for col, expected_dtype in EXPECTED_SCHEMA.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(expected_dtype)
            except Exception as e:
                logging.warning(f"⚠️ Data type mismatch in column {col}: {e}")
    
    return df

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data:
    - Cleans & maps column names dynamically
    - Ensures all columns exist
    - Converts numeric fields safely
    - Provides business insights in a structured format
    """
    df = clean_column_names(df)
    missing_columns = validate_columns(df)

    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns} (Check CSV Formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    df = validate_data_types(df)

    # Convert CTR percentages into decimal format
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': df['impressions'].sum(),
        'total_clicks': df['clicks'].sum(),
        'average_ctr': df['ctr'].mean() * 100 if 'ctr' in df.columns else 0,
        'total_conversions': df['conversions'].sum(),
        'total_conversion_value': df['conversion_value'].sum() if 'conversion_value' in df.columns else 0,
    }

    logging.info("✅ Successfully processed data insights")
    return insights, df
