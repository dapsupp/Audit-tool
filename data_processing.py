import pandas as pd
import logging

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

    # ✅ Compute overall metrics
    total_conversion_value = df["conversion_value"].sum() if "conversion_value" in df.columns else 0
    total_cost = df["cost"].sum() if "cost" in df.columns else 0

    # ✅ Debugging: Print values before computing ROAS
    print(f"DEBUG - Total Conversion Value: {total_conversion_value}")
    print(f"DEBUG - Total Cost: {total_cost}")

    # ✅ Compute ROAS using the correct formula
    roas = total_conversion_value / total_cost if total_cost > 0 else 0  

    # ✅ Store Correct ROAS in insights
    insights = {
        "total_item_count": df.shape[0],
        "total_impressions": df["impressions"].sum() if "impressions" in df.columns else 0,
        "total_clicks": df["clicks"].sum() if "clicks" in df.columns else 0,
        "total_conversions": df["conversions"].sum() if "conversions" in df.columns else 0,
        "total_conversion_value": total_conversion_value,
        "total_cost": total_cost,
        "average_search_impression_share": df["search_impression_share"].mean() if "search_impression_share" in df.columns else 0,
        "average_ctr": df["ctr"].mean() * 100 if "ctr" in df.columns else 0,
        "roas": round(roas, 2),
    }

    # ✅ Debugging: Print the final computed ROAS
    print(f"DEBUG - Computed ROAS: {insights['roas']}")

    return insights, df  # ✅ Ensure we return both values
