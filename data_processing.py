import pandas as pd
import logging

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes DataFrame column names to lowercase with underscores.
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
        'search_impr_share': 'search_impression_share',
        'search_impr__share': 'search_impression_share',  # Ensure variations are handled
        'cost': 'cost'
    }
    
    df.rename(columns=rename_mapping, inplace=True)
    
    return df

def calculate_funnel_metrics(df: pd.DataFrame):
    """
    Calculates full-funnel efficiency:
    - Avg impressions per click
    - Number of products achieving this rate
    - Avg clicks per conversion
    - Number of products achieving this rate
    """
    if "impressions" in df.columns and "clicks" in df.columns and "conversions" in df.columns:
        df["impressions_per_click"] = df["impressions"] / df["clicks"]
        df["clicks_per_conversion"] = df["clicks"] / df["conversions"]

        # Handle division by zero and infinite values
        df.replace([float("inf"), -float("inf")], None, inplace=True)

        # Compute funnel averages
        avg_impressions_per_click = df["impressions_per_click"].mean()
        avg_clicks_per_conversion = df["clicks_per_conversion"].mean()

        # Find how many products meet or exceed these averages
        num_products_meeting_impressions_per_click = df[df["impressions_per_click"] <= avg_impressions_per_click].shape[0]
        num_products_meeting_clicks_per_conversion = df[df["clicks_per_conversion"] <= avg_clicks_per_conversion].shape[0]

        # Return insights
        funnel_metrics = {
            "avg_impressions_per_click": round(avg_impressions_per_click, 2),
            "num_products_meeting_impressions_per_click": num_products_meeting_impressions_per_click,
            "avg_clicks_per_conversion": round(avg_clicks_per_conversion, 2),
            "num_products_meeting_clicks_per_conversion": num_products_meeting_clicks_per_conversion,
        }
        return funnel_metrics
    else:
        return {
            "avg_impressions_per_click": None,
            "num_products_meeting_impressions_per_click": None,
            "avg_clicks_per_conversion": None,
            "num_products_meeting_clicks_per_conversion": None,
        }

def assess_product_performance(df: pd.DataFrame):
    """
    Processes and cleans Google Ads data for performance analysis.
    """
    df = clean_column_names(df)

    # Convert numeric columns safely
    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'conversion_value_cost', 'search_impression_share', 'cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)

    # Compute funnel metrics
    funnel_metrics = calculate_funnel_metrics(df)  # ✅ Ensure this is called

    # Return insights
    insights = {
        "total_item_count": df.shape[0],
        "total_impressions": df["impressions"].sum() if "impressions" in df.columns else 0,
        "total_clicks": df["clicks"].sum() if "clicks" in df.columns else 0,
        "total_conversions": df["conversions"].sum() if "conversions" in df.columns else 0,
        **funnel_metrics,  # ✅ Merge funnel metrics
    }

    return insights, df  # ✅ Ensure we return both values
