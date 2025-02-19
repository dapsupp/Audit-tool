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

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google PMAX campaign data and extracts insights.
    """
    df = clean_column_names(df)

    # Convert 'conversion_value' and 'cost' to numeric safely
    df['conversion_value'] = pd.to_numeric(df['conversion_value'].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
    df['cost'] = pd.to_numeric(df['cost'].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)

    total_conversion_value = df['conversion_value'].sum()
    total_cost = df['cost'].sum()

    df_sorted = df.sort_values(by='conversion_value', ascending=False)  # Sort by revenue

    sku_thresholds = [5, 10, 20, 50]  # Define SKU performance tiers
    sku_contribution = {}

    if total_conversion_value > 0 and 'conversion_value' in df.columns and 'cost' in df.columns:
        for threshold in sku_thresholds:
            num_skus = int(df.shape[0] * (threshold / 100))  # Convert % to actual SKU count
            top_n_skus = df_sorted.head(num_skus)

            # Revenue contribution
            conversion_value = top_n_skus['conversion_value'].sum()
            contribution_percentage = (conversion_value / total_conversion_value * 100) if total_conversion_value > 0 else 0

            # ROAS Calculation
            total_cost_tier = top_n_skus['cost'].sum()
            roas = (conversion_value / total_cost_tier) if total_cost_tier > 0 else 0  # Prevent division by zero

            # Store results in dictionary format
            sku_contribution[f'top_{threshold}_sku_contribution'] = {
                "sku_count": num_skus,
                "percentage": round(contribution_percentage, 2),
                "conversion_value": round(conversion_value, 2),
                "roas": round(roas, 2),
            }

    return sku_contribution
