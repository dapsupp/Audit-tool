import pandas as pd
import numpy as np
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
    
    # Log unmapped columns for debugging
    unmapped = [col for col in df.columns if col not in rename_mapping.values()]
    if unmapped:
        logging.info(f"Unmapped columns detected: {unmapped}")
    
    return df

def calculate_funnel_metrics(df: pd.DataFrame):
    """
    Calculates full-funnel efficiency with performance categorization and variance analysis.
    """
    total_products = df.shape[0]
    if "impressions" in df.columns and "clicks" in df.columns and "conversions" in df.columns:
        # Calculate impressions_per_click for products with clicks > 0
        df['impressions_per_click'] = df.apply(
            lambda row: row['impressions'] / row['clicks'] if row['clicks'] > 0 else None, axis=1
        )
        # Calculate clicks_per_conversion for products with conversions > 0
        df['clicks_per_conversion'] = df.apply(
            lambda row: row['clicks'] / row['conversions'] if row['conversions'] > 0 else None, axis=1
        )

        # Calculate averages
        avg_ipc = df['impressions_per_click'].mean() if df['impressions_per_click'].notnull().any() else 0
        avg_cpc = df['clicks_per_conversion'].mean() if df['clicks_per_conversion'].notnull().any() else 0

        # Calculate standard deviations
        std_ipc = df['impressions_per_click'].std() if df['impressions_per_click'].notnull().any() else 0
        std_cpc = df['clicks_per_conversion'].std() if df['clicks_per_conversion'].notnull().any() else 0

        # Categorize impressions per click
        conditions_ipc = [
            (df['clicks'] > 0) & (df['impressions_per_click'] <= avg_ipc * 0.9),
            (df['clicks'] > 0) & (df['impressions_per_click'] > avg_ipc * 0.9) & (df['impressions_per_click'] <= avg_ipc * 1.1),
            (df['clicks'] > 0) & (df['impressions_per_click'] > avg_ipc * 1.1),
            df['clicks'] == 0
        ]
        choices_ipc = ['High', 'Moderate', 'Low', 'Low']
        df['ipc_category'] = np.select(conditions_ipc, choices_ipc, default='Unknown')

        # Categorize clicks per conversion
        conditions_cpc = [
            (df['conversions'] > 0) & (df['clicks_per_conversion'] <= avg_cpc * 0.9),
            (df['conversions'] > 0) & (df['clicks_per_conversion'] > avg_cpc * 0.9) & (df['clicks_per_conversion'] <= avg_cpc * 1.1),
            (df['conversions'] > 0) & (df['clicks_per_conversion'] > avg_cpc * 1.1),
            df['conversions'] == 0
        ]
        choices_cpc = ['High', 'Moderate', 'Low', 'Low']
        df['cpc_category'] = np.select(conditions_cpc, choices_cpc, default='Unknown')

        # Calculate category counts
        ipc_category_counts = df['ipc_category'].value_counts()
        cpc_category_counts = df['cpc_category'].value_counts()

        # Get counts for each category
        ipc_high_count = ipc_category_counts.get('High', 0)
        ipc_moderate_count = ipc_category_counts.get('Moderate', 0)
        ipc_low_count = ipc_category_counts.get('Low', 0)

        cpc_high_count = cpc_category_counts.get('High', 0)
        cpc_moderate_count = cpc_category_counts.get('Moderate', 0)
        cpc_low_count = cpc_category_counts.get('Low', 0)

        # Log category counts for debugging
        logging.info(f"IPC Categories: High={ipc_high_count}, Moderate={ipc_moderate_count}, Low={ipc_low_count}")
        logging.info(f"CPC Categories: High={cpc_high_count}, Moderate={cpc_moderate_count}, Low={cpc_low_count}")

        # Calculate percentages
        ipc_high_percent = (ipc_high_count / total_products * 100) if total_products > 0 else 0
        ipc_moderate_percent = (ipc_moderate_count / total_products * 100) if total_products > 0 else 0
        ipc_low_percent = (ipc_low_count / total_products * 100) if total_products > 0 else 0

        cpc_high_percent = (cpc_high_count / total_products * 100) if total_products > 0 else 0
        cpc_moderate_percent = (cpc_moderate_count / total_products * 100) if total_products > 0 else 0
        cpc_low_percent = (cpc_low_count / total_products * 100) if total_products > 0 else 0

        return {
            "avg_impressions_per_click": round(avg_ipc, 2),
            "std_impressions_per_click": round(std_ipc, 2),
            "ipc_high_count": ipc_high_count,
            "ipc_high_percent": round(ipc_high_percent, 2),
            "ipc_moderate_count": ipc_moderate_count,
            "ipc_moderate_percent": round(ipc_moderate_percent, 2),
            "ipc_low_count": ipc_low_count,
            "ipc_low_percent": round(ipc_low_percent, 2),
            "avg_clicks_per_conversion": round(avg_cpc, 2),
            "std_clicks_per_conversion": round(std_cpc, 2),
            "cpc_high_count": cpc_high_count,
            "cpc_high_percent": round(cpc_high_percent, 2),
            "cpc_moderate_count": cpc_moderate_count,
            "cpc_moderate_percent": round(cpc_moderate_percent, 2),
            "cpc_low_count": cpc_low_count,
            "cpc_low_percent": round(cpc_low_percent, 2),
        }
    else:
        # Return default values if required columns are missing
        return {
            "avg_impressions_per_click": 0,
            "std_impressions_per_click": 0,
            "ipc_high_count": 0,
            "ipc_high_percent": 0,
            "ipc_moderate_count": 0,
            "ipc_moderate_percent": 0,
            "ipc_low_count": 0,
            "ipc_low_percent": 0,
            "avg_clicks_per_conversion": 0,
            "std_clicks_per_conversion": 0,
            "cpc_high_count": 0,
            "cpc_high_percent": 0,
            "cpc_moderate_count": 0,
            "cpc_moderate_percent": 0,
            "cpc_low_count": 0,
            "cpc_low_percent": 0,
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

    # Ensure 'search_impression_share' is correctly processed
    if "search_impression_share" in df.columns:
        df["search_impression_share"] = df["search_impression_share"].astype(str)
        df["search_impression_share"] = (
            df["search_impression_share"]
            .replace("--", None)
            .replace("< 10", "5")
            .str.rstrip("%")
        )
        df["search_impression_share"] = pd.to_numeric(df["search_impression_share"], errors="coerce")
        average_search_impr_share = df["search_impression_share"].mean()
    else:
        average_search_impr_share = 0

    # Fix: Clean CTR column to remove % and handle both integer and decimal values
    if "ctr" in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.replace('%', '', regex=False)
        df['ctr'] = df['ctr'].str.extract(r'(\d+\.?\d*)')  # Handles both integer and decimal values
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce').fillna(0) / 100
        average_ctr = df["ctr"].mean() * 100 if "ctr" in df.columns else 0
    else:
        average_ctr = 0

    # Compute overall metrics
    total_conversion_value = df["conversion_value"].sum() if "conversion_value" in df.columns else 0
    total_cost = df["cost"].sum() if "cost" in df.columns else 0
    roas = total_conversion_value / total_cost if total_cost > 0 else 0

    # Compute Pareto Law SKU Contribution Breakdown
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

    # Compute funnel metrics (enhanced with categorization and variance)
    funnel_metrics = calculate_funnel_metrics(df)

    # Ensure the function returns both insights & the processed DataFrame
    insights = {
        "total_item_count": df.shape[0],
        "total_impressions": df["impressions"].sum() if "impressions" in df.columns else 0,
        "total_clicks": df["clicks"].sum() if "clicks" in df.columns else 0,
        "total_conversions": df["conversions"].sum() if "conversions" in df.columns else 0,
        "total_conversion_value": total_conversion_value,
        "total_cost": total_cost,
        "average_search_impression_share": round(average_search_impr_share, 2),
        "average_ctr": round(average_ctr, 2),
        "roas": round(roas, 2),
        **sku_contribution,
        **funnel_metrics,  # Merge enhanced funnel metrics
    }

    return insights, df
