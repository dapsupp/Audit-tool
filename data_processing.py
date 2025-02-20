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

    # ✅ Ensure 'search_impression_share' is correctly processed
    if "search_impression_share" in df.columns:
        df["search_impression_share"] = df["search_impression_share"].astype(str)

        # Handle missing values and "< 10" cases
        df["search_impression_share"] = (
            df["search_impression_share"]
            .replace("--", None)  # Convert "--" to NaN
            .replace("< 10", "5")  # Convert "< 10" to midpoint value (5%)
            .str.rstrip("%")  # Remove percentage symbols
        )

        # Convert to numeric format safely
        df["search_impression_share"] = pd.to_numeric(df["search_impression_share"], errors="coerce")

        # ✅ Ensure Search Impression Share is correctly averaged
        average_search_impr_share = df["search_impression_share"].mean()
    else:
        average_search_impr_share = 0  # Default to 0 if column is missing

    # ✅ Fix: Clean CTR column to remove % and handle concatenated values
    if "ctr" in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.replace('%', '', regex=False)  # Remove % symbols
        df['ctr'] = df['ctr'].str.extract(r'(\d+\.\d+)')  # Extract only numeric values
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce').fillna(0) / 100  # Convert to decimal format

        # ✅ Ensure 'average_ctr' is included in insights
        average_ctr = df["ctr"].mean() * 100 if "ctr" in df.columns else 0
    else:
        average_ctr = 0  # Default to 0 if column is missing

    # ✅ Compute overall metrics
    total_conversion_value = df["conversion_value"].sum() if "conversion_value" in df.columns else 0
    total_cost = df["cost"].sum() if "cost" in df.columns else 0

    # ✅ Debugging: Print values to verify correctness
    print(f"DEBUG - Total Conversion Value: {total_conversion_value}")
    print(f"DEBUG - Total Cost: {total_cost}")

    # ✅ Correct ROAS Calculation
    roas = total_conversion_value / total_cost if total_cost > 0 else 0  

    # ✅ Store Correct ROAS in insights
    insights = {
        "total_conversion_value": total_conversion_value,
        "total_cost": total_cost,
        "roas": round(roas, 2),  # ✅ Ensure rounding happens only after division
    }

    # ✅ Debugging: Print the final computed ROAS
    print(f"DEBUG - Computed ROAS: {roas}")

    # ✅ Compute funnel metrics (Inventory Marketing Funnel)
    funnel_metrics = calculate_funnel_metrics(df)

    # ✅ Ensure the function returns both insights & the processed DataFrame
    insights.update(funnel_metrics)  # ✅ Merge funnel metrics

    return insights, df  # ✅ Ensure we return both values
