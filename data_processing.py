import pandas as pd

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure column names are formatted correctly."""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=True)

    rename_map = {
        'item_id': 'item id',
        'impressions': 'impr.',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'conversions': 'conversions',
        'conversion value': 'conv. value',
        'conversion value / cost': 'conv. value / cost',
        'search impression share': 'search impr. share'
    }
    df.rename(columns=rename_map, inplace=True)
    return df

def assess_product_performance(df: pd.DataFrame):
    """Assess product-level performance in Google PMAX campaigns."""
    df = clean_column_names(df)

    numeric_columns = ['impr.', 'clicks', 'conversions', 'conv. value']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert percentage strings to floats
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': df['impr.'].sum(),
        'total_clicks': df['clicks'].sum(),
        'average_ctr': df['ctr'].mean() * 100 if 'ctr' in df.columns else 0,
        'total_conversions': df['conversions'].sum(),
        'total_conversion_value': df['conv. value'].sum(),
    }

    return insights, df
