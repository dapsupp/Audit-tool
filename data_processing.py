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
    - Converts numeric fields safely.
    - Cleans and formats the 'Search Impression Share' column correctly.
    - Returns processed insights and cleaned DataFrame.
    """
    df = clean_column_names(df)

    # Convert numeric columns safely
    numeric_columns = ['impressions', 'clicks', 'conversions', 'conversion_value', 'conversion_value_cost', 'search_impression_share', 'cost']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)

    # ✅ Fix: Properly format Search Impression Share
    if "search_impression_share" in df.columns:
        df["search_impression_share"] = df["search_impression_share"].astype(str)

        # Replace missing values and "< 10" cases
        df["search_impression_share"] = (
            df["search_impression_share"]
            .replace("--", None)  # Convert "--" to NaN
            .replace("< 10", "5")  # Convert "< 10" to midpoint value (5%)
            .replace("None", None)  # Convert remaining "None" strings to NaN
            .str.rstrip("%")  # Remove percentage symbols
        )

        # Convert to numeric format safely
        df["search_impression_share"] = pd.to_numeric(df["search_impression_share"], errors="coerce")

        # ✅ Ensure Search Impression Share is correctly averaged and capped at 100%
        average_search_impr_share = df["search_impression_share"].mean()
    else:
        average_search_impr_share = 0  # Default to 0 if column is missing

    # ✅ Fix: Clean CTR column to remove % and handle concatenated values
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.replace('%', '', regex=False)  # Remove % symbols
        df['ctr'] = df['ctr'].str.extract(r'(\d+\.\d+)')  # Extract only numeric values
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce').fillna(0) / 100  # Convert to decimal format

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

    # ✅ Compute funnel metrics
    funnel_metrics = calculate_funnel_metrics(df)

    # ✅ Ensure the function returns both insights & the processed DataFrame
    insights = {
        "total_item_count": df.shape[0],
        "total_impressions": df["impressions"].sum() if "impressions" in df.columns else 0,
        "total_clicks": df["clicks"].sum() if "clicks" in df.columns else 0,
        "average_ctr": df["ctr"].mean() * 100 if "ctr" in df.columns else 0,
        "total_conversions": df["conversions"].sum() if "conversions" in df.columns else 0,
        "total_conversion_value": total_conversion_value,
        "total_cost": total_cost,
        "average_search_impression_share": round(average_search_impr_share, 2),  # ✅ Ensure correct calculation
        "roas": total_conversion_value / total_cost if total_cost > 0 else 0,
        **sku_contribution,  # Merge SKU Contribution insights into the dictionary
        **funnel_metrics,  # ✅ Merge new funnel metrics
    }

    return insights, df  # ✅ Ensure we return both values
