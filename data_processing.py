import pandas as pd 
import difflib
import logging
from thefuzz import process

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame's column names by:
    - Stripping whitespace
    - Converting to lowercase
    - Replacing spaces and dots with underscores
    - Mapping common abbreviations to expected names
    """
    # Standardise column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('.', '_')
    )
    
    # Mapping dictionary: key is the cleaned column name, value is the required name
    rename_mapping = {
        'impr_': 'impressions',
        'conv__value': 'conversion_value',
        'conv__value___cost': 'conversion_value_cost',
    }
    
    # Rename columns based on the mapping
    df.rename(columns=rename_mapping, inplace=True)
    
    return df

def validate_columns(df: pd.DataFrame) -> list:
    """
    Validates that the required columns exist in the DataFrame.
    If any required columns are missing, returns a list of them.
    """
    # Define the required columns for analysis
    required_columns = ['impressions', 'clicks', 'ctr', 'conversions', 'conversion_value', 'conversion_value_cost']
    
    missing = []
    for col in required_columns:
        if col not in df.columns:
            # Optionally, find close matches for guidance
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
    - Converts numeric fields safely
    - Provides business insights
    """
    # Clean and standardise column names
    df = clean_column_names(df)
    
    # Validate that the necessary columns are present
    missing_columns = validate_columns(df)
    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns} (Check CSV Formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    # Convert numeric values safely (handling cases where they are stored as strings)
    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'conversion_value_cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)  # Convert to float, replace errors with 0

    # Convert CTR percentages into decimal format
    if 'ctr' in df.columns:
        # Remove the percentage sign and convert to float, then to a decimal representation
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
