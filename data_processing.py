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

# Expected column mappings
EXPECTED_COLUMNS = {
    'item_id': 'item_id',
    'impr.': 'impressions',
    'clicks': 'clicks',
    'ctr': 'ctr',
    'conversions': 'conversions',
    'conv. value': 'conversion_value',
    'conv_value': 'conversion_value',
    'conversion value': 'conversion_value',
    'conv. value / cost': 'conversion_value_cost',
    'search impr. share': 'search_impr_share'
}

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names:
    - Converts all to lowercase
    - Removes spaces
    - Uses fuzzy matching for incorrect names
    - Handles cases where fuzzy matching fails
    """

    # Ensure at least one column exists
    if df.empty or len(df.columns) == 0:
        logging.error("🚨 Error: CSV does not contain valid column headers.")
        raise ValueError("Uploaded CSV does not have valid column headers.")

    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    renamed_columns = {}
    for col in df.columns:
        if not col.strip():  # Handle empty column names
            logging.warning(f"⚠️ Empty column name found: {col}")
            renamed_columns[col] = f"unknown_column_{len(renamed_columns) + 1}"
            continue

        match_result = process.extractOne(col, EXPECTED_COLUMNS.keys(), score_cutoff=75)

        if match_result:  # Ensure we have a valid match
            match = match_result[0]  # Only extract match, ignore score
            renamed_columns[col] = EXPECTED_COLUMNS.get(match, match)  # Use expected name if available
        else:
            renamed_columns[col] = col  # Keep unchanged if no match found

    df.rename(columns=renamed_columns, inplace=True)
    logging.info(f"✅ Column Mapping Applied: {renamed_columns}")

    return df

def validate_columns(df: pd.DataFrame) -> list:
    """
    Ensures all required columns exist post-cleaning.
    """
    required_columns = list(EXPECTED_COLUMNS.values())
    missing_columns = [col for col in required_columns if col not in df.columns]

    return missing_columns

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
