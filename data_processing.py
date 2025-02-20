import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes DataFrame column names.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(r"[ .]", "_", regex=True)

    rename_mapping = {
        "impr_": "impressions",
        "conv__value": "conversion_value",
        "conv__value_/_cost": "conversion_value_cost",
        "search_impr_share": "search_impression_share",
        "search_impr__share": "search_impression_share",
    }

    df.rename(columns=rename_mapping, inplace=True)
    return df

def convert_numeric_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Converts specific columns to numeric format safely.
    """
    for col in columns:
        if (col in df.columns):
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").fillna(0)
    return df

def assess_product_performance(df: pd.DataFrame):
    """
    Processes Google Ads data for performance analysis.
    """
    df = clean_column_names(df)
    numeric_cols = ["impressions", "clicks", "conversions", "conversion_value", "cost"]
    df = convert_numeric_columns(df, numeric_cols)

    insights = {
    "total_conversion_value": df["conversion_value"].sum() if "conversion_value" in df.columns else 0,
    "total_cost": df["cost"].sum() if "cost" in df.columns else 0,
    "total_item_count": len(df),  # Total number of rows
    "total_impressions": df["impressions"].sum() if "impressions" in df.columns else 0
    }
    
    insights["roas"] = (insights["total_conversion_value"] / insights["total_cost"]) if insights["total_cost"] > 0 else 0
    insights["roas"] = insights["total_conversion_value"] / insights["total_cost"] if insights["total_cost"] > 0 else 0

    logging.info(f"Insights: {insights}")
    return insights, df
