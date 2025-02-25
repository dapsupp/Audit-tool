import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def display_account_summary():
    """
    Displays the Account Summary page, allowing users to upload a CSV file and view key metrics and trends.
    """
    st.subheader("📅 Account Summary")
    account_summary_file = st.file_uploader(
        "📤 Upload your Account Summary CSV file", 
        type="csv", 
        key="account_summary_uploader"
    )
    
    if account_summary_file:
        try:
            # Read the CSV file
            df_summary = pd.read_csv(account_summary_file, encoding="utf-8", on_bad_lines="skip")
            
            # Validate required columns
            required_columns = ["Month", "Conv. value", "Currency code", "Cost", "Conv. value / cost"]
            df_summary.columns = df_summary.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '_')
            missing_columns = [col for col in required_columns if col.lower().replace(' ', '_').replace('.', '_') not in df_summary.columns]
            if missing_columns:
                st.error(f"⚠️ Missing columns: {', '.join(missing_columns)}")
            else:
                # Clean and prepare data
                df_summary['month'] = pd.to_datetime(df_summary['month'], errors='coerce')
                numeric_cols = ["conv_value", "cost", "conv_value_cost"]
                for col in numeric_cols:
                    df_summary[col] = pd.to_numeric(df_summary[col], errors='coerce')
                
                # Drop rows with missing critical data
                df_summary = df_summary.dropna(subset=['month', 'conv_value', 'cost', 'conv_value_cost'])
                
                # Sort by month
                df_summary = df_summary.sort_values('month')
                
                # Check currency consistency
                unique_currencies = df_summary['currency_code'].unique()
                if len(unique_currencies) > 1:
                    st.warning("⚠️ Multiple currencies detected. Please ensure all data is in the same currency.")
                else:
                    currency = unique_currencies[0]
                    st.info(f"💱 All data is in {currency}.")

                # Calculate key metrics
                total_conv_value = df_summary['conv_value'].sum()
                total_cost = df_summary['cost'].sum()
                overall_conv_value_cost = total_conv_value / total_cost if total_cost > 0 else 0

                # Display metrics
                st.subheader("📊 Account Summary Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Conversion Value", f"{currency} {total_conv_value:,.2f}")
                with col2:
                    st.metric("Total Cost", f"{currency} {total_cost:,.2f}")
                with col3:
                    st.metric("Overall Conv.value/cost", f"{overall_conv_value_cost:.2f}")

                # Visualize trends
                st.subheader("📈 Trends over Time")
                
                # Chart 1: Conv.value and Cost
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(x=df_summary['month'], y=df_summary['conv_value'], mode='lines+markers', name='Conv.value'))
                fig1.add_trace(go.Scatter(x=df_summary['month'], y=df_summary['cost'], mode='lines+markers', name='Cost'))
                fig1.update_layout(title='Conversion Value and Cost over Time', xaxis_title='Month', yaxis_title='Amount')
                st.plotly_chart(fig1, use_container_width=True)
                
                # Chart 2: Conv.value/cost
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df_summary['month'], y=df_summary['conv_value_cost'], mode='lines+markers', name='Conv.value/cost'))
                fig2.update_layout(title='Conv.value/cost over Time', xaxis_title='Month', yaxis_title='Ratio')
                st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error processing account summary: {e}")
