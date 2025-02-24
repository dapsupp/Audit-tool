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
        'search_impr__share': 'search_impression_share',  # Handle variations
        'cost': 'cost'
    }
    
    df.rename(columns=rename_mapping, inplace=True)
    
    return df

def calculate_funnel_metrics(df: pd.DataFrame):
    """
    Calculates marketing funnel efficiency metrics:
    - Average impressions per click across products
    - Number and percentage of products meeting or exceeding this average
    - Average clicks per conversion across products
    - Number and percentage of products meeting or exceeding this average
    """
    total_products = df.shape[0]
    if "impressions" in df.columns and "clicks" in df.columns and "conversions" in df.columns:
        # Calculate per-product metrics
        df["impressions_per_click"] = df["impressions"] / df["clicks"].replace(0, 1)  # Avoid division by zero
        df["clicks_per_conversion"] = df["clicks"] / df["conversions"].replace(0, 1)  # Avoid division by zero

        # Handle infinite values
        df["impressions_per_click"].replace([float("inf"), -float("inf")], None, inplace=True)
        df["clicks_per_conversion"].replace([float("inf"), -float("inf")], None, inplace=True)

        # Compute averages across products
        avg_impressions_per_click = df["impressions_per_click"].mean()
        avg_clicks_per_conversion = df["clicks_per_conversion"].mean()

        # Count products meeting or exceeding averages (lower is better)
        if pd.notnull(avg_impressions_per_click):
            num_products_meeting_impressions = df[df["impressions_per_click"] <= avg_impressions_per_click].shape[0]
        else:
            num_products_meeting_impressions = 0

        if pd.notnull(avg_clicks_per_conversion):
            num_products_meeting_clicks = df[df["clicks_per_conversion"] <= avg_clicks_per_conversion].shape[0]
        else:
            num_products_meeting_clicks = 0

        # Calculate percentages
        percent_meeting_impressions = (num_products_meeting_impressions / total_products * 100) if total_products > 0 else 0
        percent_meeting_clicks = (num_products_meeting_clicks / total_products * 100) if total_products > 0 else 0

        # Return funnel metrics
        return {
            "avg_impressions_per_click": round(avg_impressions_per_click, 2) if pd.notnull(avg_impressions_per_click) else 0,
            "num_products_meeting_impressions": num_products_meeting_impressions,
            "percent_meeting_impressions": round(percent_meeting_impressions, 2),
            "avg_clicks_per_conversion": round(avg_clicks_per_conversion, 2) if pd.notnull(avg_clicks_per_conversion) else 0,
            "num_products_meeting_clicks": num_products_meeting_clicks,
            "percent_meeting_clicks": round(percent_meeting_clicks, 2),
        }
    else:
        return {
            "avg_impressions_per_click": 0,
            "num_products_meeting_impressions": 0,
            "percent_meeting_impressions": 0,
            "avg_clicks_per_conversion": 0,
            "num_products_meeting_clicks": 0,
            "percent_meeting_clicks": 0,
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

    # Existing metrics (unchanged)
    total_impressions = df["impressions"].sum() if "impressions" in df.columns else 0
    total_clicks = df["clicks"].sum() if "clicks" in df.columns else 0
    total_conversions = df["conversions"].sum() if "conversions" in df.columns else 0
    total_item_count = df.shape[0]

    overall_impressions_per_click = total_impressions / total_clicks if total_clicks > 0 else 0
    overall_clicks_per_conversion = total_clicks / total_conversions if total_conversions > 0 else 0

    # New funnel metrics
    funnel_metrics = calculate_funnel_metrics(df)

    # Combine insights (existing + new)
    insights = {
        "total_item_count": total_item_count,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "overall_impressions_per_click": round(overall_impressions_per_click, 2),
        "overall_clicks_per_conversion": round(overall_clicks_per_conversion, 2),
        **funnel_metrics,  # Add new funnel metrics
    }

    return insights, df
