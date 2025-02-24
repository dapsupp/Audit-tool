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
        'search_impr__share': 'search_impression_share',
        'cost': 'cost'
    }
    
    df.rename(columns=rename_mapping, inplace=True)
    return df

def calculate_funnel_metrics(df: pd.DataFrame):
    """
    Calculates marketing funnel efficiency metrics:
    - Average impressions per click and clicks per conversion.
    - Number/percentage of products meeting or exceeding these averages.
    """
    total_products = df.shape[0]
    if "impressions" in df.columns and "clicks" in df.columns and "conversions" in df.columns:
        df["impressions_per_click"] = df["impressions"] / df["clicks"].replace(0, 1)
        df["clicks_per_conversion"] = df["clicks"] / df["conversions"].replace(0, 1)

        df["impressions_per_click"].replace([float("inf"), -float("inf")], None, inplace=True)
        df["clicks_per_conversion"].replace([float("inf"), -float("inf")], None, inplace=True)

        avg_impressions_per_click = df["impressions_per_click"].mean()
        avg_clicks_per_conversion = df["clicks_per_conversion"].mean()

        num_products_meeting_impressions = df[df["impressions_per_click"] <= avg_impressions_per_click].shape[0] if pd.notnull(avg_impressions_per_click) else 0
        num_products_meeting_clicks = df[df["clicks_per_conversion"] <= avg_clicks_per_conversion].shape[0] if pd.notnull(avg_clicks_per_conversion) else 0

        percent_meeting_impressions = (num_products_meeting_impressions / total_products * 100) if total_products > 0 else 0
        percent_meeting_clicks = (num_products_meeting_clicks / total_products * 100) if total_products > 0 else 0

        return {
            "avg_impressions_per_click": round(avg_impressions_per_click, 2) if pd.notnull(avg_impressions_per_click) else 0,
            "num_products_meeting_impressions": num_products_meeting_impressions,
            "percent_meeting_impressions": round(percent_meeting_impressions, 2),
            "avg_clicks_per_conversion": round(avg_clicks_per_conversion, 2) if pd.notnull(avg_clicks_per_conversion) else 0,
            "num_products_meeting_clicks": num_products_meeting_clicks,
            "percent_meeting_clicks": round(percent_meeting_clicks, 2),
        }
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
    Processes Google Ads data for performance analysis, including all original metrics.
    """
    df = clean_column_names(df)

    # Convert numeric columns
    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)

    # Original total metrics
    total_impressions = df["impressions"].sum() if "impressions" in df.columns else 0
    total_clicks = df["clicks"].sum() if "clicks" in df.columns else 0
    total_conversions = df["conversions"].sum() if "conversions" in df.columns else 0
    total_conversion_value = df["conversion_value"].sum() if "conversion_value" in df.columns else 0
    total_cost = df["cost"].sum() if "cost" in df.columns else 0
    roas = total_conversion_value / total_cost if total_cost > 0 else 0

    # Pareto Law SKU Contribution
    sku_thresholds = [5, 10, 20, 50]
    sku_contribution = {}
    if total_conversion_value > 0 and "conversion_value" in df.columns and "cost" in df.columns:
        df_sorted = df.sort_values(by="conversion_value", ascending=False)
        for threshold in sku_thresholds:
            num_skus = int(df.shape[0] * (threshold / 100))
            top_n_skus = df_sorted.head(num_skus)
            conversion_value = top_n_skus["conversion_value"].sum()
            contribution_percentage = (conversion_value / total_conversion_value * 100) if total_conversion_value > 0 else 0
            total_cost_tier = top_n_skus["cost"].sum()
            sku_roas = (conversion_value / total_cost_tier) if total_cost_tier > 0 else 0
            sku_contribution[f"top_{threshold}_sku_contribution"] = {
                "sku_count": num_skus,
                "percentage": round(contribution_percentage, 2),
                "conversion_value": round(conversion_value, 2),
                "roas": round(sku_roas, 2),
            }

    # New funnel metrics
    funnel_metrics = calculate_funnel_metrics(df)

    # Combine all insights
    insights = {
        "total_item_count": df.shape[0],
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_conversion_value": total_conversion_value,
        "total_cost": total_cost,
        "roas": round(roas, 2),
        **sku_contribution,
        **funnel_metrics,
    }

    return insights, df
