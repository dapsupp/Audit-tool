import pandas as pd
import logging
from collections import defaultdict
from typing import Tuple, Dict

def detect_header_row(file_path: str) -> int:
    """Detect the correct header row by scanning for specific column names."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if "Item ID" in line and "Impr." in line:
                    return i  # Found the header row
    except Exception as e:
        logging.error(f"Error detecting header row: {e}")
    return 0  # Fallback if not found

def process_large_csv(file_path: str, chunk_size: int = 100000) -> Tuple[Dict[str, float], Dict]:
    """
    Processes a CSV file in chunks.
    
    Returns:
      - insights: A dictionary with overall metrics.
      - sku_sales: A dictionary mapping SKU (Item ID) to total sales (conversion value).
    """
    header_row = detect_header_row(file_path)
    total_impressions = total_clicks = total_conversions = 0
    total_conversion_value = total_cost = total_search_impr_share = 0
    valid_search_impr_count = 0
    sku_sales = defaultdict(float)

    try:
        for chunk in pd.read_csv(file_path,
                                 chunksize=chunk_size,
                                 encoding="utf-8",
                                 on_bad_lines="skip",
                                 skiprows=header_row):
            # Normalize column names
            chunk.columns = chunk.columns.str.strip().str.lower()
            required_columns = ["impr.", "clicks", "conversions", "conv. value", "cost"]
            missing_columns = [col for col in required_columns if col not in chunk.columns]
            if missing_columns:
                raise ValueError(f"Missing expected columns: {', '.join(missing_columns)}")
            
            # Clean and convert numeric columns
            for col in required_columns:
                chunk[col] = pd.to_numeric(chunk[col].astype(str).str.replace(",", ""), errors='coerce').fillna(0)
            
            # Compute ROAS (vectorised)
            chunk["roas"] = chunk["conv. value"] / chunk["cost"]
            chunk.loc[chunk["cost"] <= 0, "roas"] = 0
            
            # Process Search Impression Share if available
            if "search impr. share" in chunk.columns:
                chunk["search impr. share"] = pd.to_numeric(
                    chunk["search impr. share"].astype(str).str.replace("%", "").replace("--", ""),
                    errors='coerce'
                )
            else:
                chunk["search impr. share"] = pd.NA

            # Aggregate metrics
            total_impressions += chunk["impr."].sum()
            total_clicks += chunk["clicks"].sum()
            total_conversions += chunk["conversions"].sum()
            total_conversion_value += chunk["conv. value"].sum()
            total_cost += chunk["cost"].sum()
            
            valid_search_chunk = chunk["search impr. share"].dropna()
            total_search_impr_share += valid_search_chunk.sum()
            valid_search_impr_count += valid_search_chunk.count()
            
            # Aggregate SKU sales (using "item id" as the key)
            if "item id" in chunk.columns:
                sku_group = chunk.groupby("item id")["conv. value"].sum()
                for sku, sale in sku_group.items():
                    sku_sales[sku] += sale

    except Exception as e:
        logging.error(f"Error processing CSV file: {e}")
        raise e

    # Compute Pareto analysis: determine SKUs driving 80% of total sales
    pareto_threshold = 0.8 * total_conversion_value if total_conversion_value else 0
    sorted_skus = sorted(sku_sales.items(), key=lambda x: x[1], reverse=True)
    accumulated_sales = 0
    sku_count_for_pareto = 0
    for sku, sale in sorted_skus:
        accumulated_sales += sale
        sku_count_for_pareto += 1
        if accumulated_sales >= pareto_threshold:
            break
    total_unique_skus = len(sku_sales)
    pareto_percentage = (sku_count_for_pareto / total_unique_skus * 100) if total_unique_skus else 0

    average_roas = total_conversion_value / total_cost if total_cost > 0 else 0
    average_search_impr_share = (total_search_impr_share / valid_search_impr_count) if valid_search_impr_count > 0 else 0

    insights = {
        "Total Impressions": total_impressions,
        "Total Clicks": total_clicks,
        "Total Conversions": total_conversions,
        "Total Conversion Value": total_conversion_value,
        "Total Cost": total_cost,
        "Average ROAS": round(average_roas, 2),
        "Average Search Impression Share": round(average_search_impr_share, 2),
        "SKUs Driving 80% Sales": sku_count_for_pareto,
        "Percentage of SKUs Driving 80% Sales": round(pareto_percentage, 2)
    }
    
    return insights, sku_sales
