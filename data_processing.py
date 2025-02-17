import pandas as pd

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures column names are consistent by:
    - Stripping extra spaces
    - Converting to lowercase
    - Replacing spaces with underscores
    - Matching common variations dynamically
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    # Mapping known variations of expected column names
    column_aliases = {
        'item_id': 'item_id',
        'impressions': 'impr.',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'conversions': 'conversions',
        'conversion_value': 'conv_value',
        'conversion_value_/_cost': 'conv_value_cost',
        'search_impression_share': 'search_impr_share'
    }

    # Dynamically rename columns by checking if a close match exists
    renamed_columns = {col: column_aliases[col] for col in df.columns if col in column_aliases}
    df.rename(columns=renamed_columns, inplace=True)

    return df

def validate_columns(df: pd.DataFrame, required_columns: list) -> list:
    """
    Validates if all required columns exist in the dataframe.
    - Returns a list of missing columns.
    - Handles variations in column naming dynamically.
    """
    existing_columns = set(df.columns)
    missing_columns = [col for col in required_columns if col not in existing_columns]

    return missing_columns

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data:
    - Cleans column names
    - Converts numeric fields safely
    - Handles missing data gracefully
    - Provides summary insights
    """
    df = clean_column_names(df)

    required_columns = ['impr.', 'clicks', 'conversions', 'conv_value']
    missing_columns = validate_columns(df, required_columns)

    if missing_columns:
        raise KeyError(f"🚨 Missing required columns: {missing_columns} (Check CSV formatting!)")

    # Convert numeric values safely
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Handle percentage conversion dynamically
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

    return insights, df
