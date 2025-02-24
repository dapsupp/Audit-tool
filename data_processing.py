import pandas as pd

def assess_product_performance(df: pd.DataFrame):
    """
    Assess product performance and compute funnel metrics.
    """
    # Existing overall totals (preserving current functionality)
    total_impressions = df["impressions"].sum() if "impressions" in df.columns else 0
    total_clicks = df["clicks"].sum() if "clicks" in df.columns else 0
    total_conversions = df["conversions"].sum() if "conversions" in df.columns else 0
    total_item_count = df.shape[0]

    # Calculate overall metrics (existing functionality)
    overall_impressions_per_click = (
        total_impressions / total_clicks if total_clicks > 0 else 0
    )
    overall_clicks_per_conversion = (
        total_clicks / total_conversions if total_conversions > 0 else 0
    )

    # Calculate funnel metrics (new and enhanced functionality)
    funnel_metrics = calculate_funnel_metrics(df)

    # Combine all insights
    insights = {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_item_count": total_item_count,
        "overall_impressions_per_click": round(overall_impressions_per_click, 2),
        "overall_clicks_per_conversion": round(overall_clicks_per_conversion, 2),
        **funnel_metrics  # Merge new funnel metrics
    }
    return insights

def calculate_funnel_metrics(df: pd.DataFrame):
    """
    Calculate per-product funnel metrics, including averages and efficiency counts/percentages.
    """
    total_products = df.shape[0]
    if "impressions" in df.columns and "clicks" in df.columns and "conversions" in df.columns:
        # Calculate per-product metrics
        df["impressions_per_click"] = df["impressions"] / df["clicks"]
        df["clicks_per_conversion"] = df["clicks"] / df["conversions"]

        # Handle division by zero and infinite values
        df["impressions_per_click"].replace([float("inf"), -float("inf")], None, inplace=True)
        df["clicks_per_conversion"].replace([float("inf"), -float("inf")], None, inplace=True)

        # Compute averages across products
        avg_impressions_per_click = df["impressions_per_click"].mean()
        avg_clicks_per_conversion = df["clicks_per_conversion"].mean()

        # Count products meeting or exceeding averages (lower is better)
        if pd.notnull(avg_impressions_per_click):
            num_products_meeting_impressions = df[
                df["impressions_per_click"] <= avg_impressions_per_click
            ].shape[0]
        else:
            num_products_meeting_impressions = 0

        if pd.notnull(avg_clicks_per_conversion):
            num_products_meeting_clicks = df[
                df["clicks_per_conversion"] <= avg_clicks_per_conversion
            ].shape[0]
        else:
            num_products_meeting_clicks = 0

        # Calculate percentages
        percent_meeting_impressions = (
            (num_products_meeting_impressions / total_products * 100)
            if total_products > 0 else 0
        )
        percent_meeting_clicks = (
            (num_products_meeting_clicks / total_products * 100)
            if total_products > 0 else 0
        )

        # Return enhanced funnel metrics
        return {
            "avg_impressions_per_click": (
                round(avg_impressions_per_click, 2) if pd.notnull(avg_impressions_per_click) else 0
            ),
            "num_products_meeting_impressions": num_products_meeting_impressions,
            "percent_meeting_impressions": round(percent_meeting_impressions, 2),
            "avg_clicks_per_conversion": (
                round(avg_clicks_per_conversion, 2) if pd.notnull(avg_clicks_per_conversion) else 0
            ),
            "num_products_meeting_clicks": num_products_meeting_clicks,
            "percent_meeting_clicks": round(percent_meeting_clicks, 2),
        }
    else:
        # Return defaults if required columns are missing
        return {
            "avg_impressions_per_click": 0,
            "num_products_meeting_impressions": 0,
            "percent_meeting_impressions": 0,
            "avg_clicks_per_conversion": 0,
            "num_products_meeting_clicks": 0,
            "percent_meeting_clicks": 0,
        }
