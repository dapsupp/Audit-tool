def assess_product_performance(df: pd.DataFrame):
    """
    Fully optimized processing of Google PMAX campaign data:
    - Cleans column names dynamically
    - Ensures all columns exist
    - Converts numeric fields safely
    - Provides business insights in a structured format
    """
    df = clean_column_names(df)
    missing_columns = validate_columns(df)

    if missing_columns:
        error_message = f"🚨 Missing Required Columns: {missing_columns} (Check CSV Formatting!)"
        logging.error(error_message)
        raise KeyError(error_message)

    # Convert numeric values safely
    numeric_cols = ['impr.', 'clicks', 'conversions', 'conv_value', 'conv_value_cost']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert CTR percentages into decimal format
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float) / 100

    insights = {
        'total_item_count': df.shape[0],
        'total_impressions': df['impr.'].sum(),
        'total_clicks': df['clicks'].sum(),
        'average_ctr': df['ctr'].mean() * 100 if 'ctr' in df.columns else 0,
        'total_conversions': df['conversions'].sum(),
        'total_conversion_value': df['conv_value'].sum() if 'conv_value' in df.columns else 0,
    }

    logging.info("✅ Successfully processed data insights")
    return insights, df  # <-- Keep this return statement, remove extra closing brace

# ✅ REMOVE THE EXTRA CLOSING BRACE HERE (which was after return insights, df)
