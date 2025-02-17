import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import tempfile
import logging
from collections import defaultdict
from typing import Tuple, Dict

# Configure logging to file for error tracking
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Ensure that table rendering works correctly
pio.renderers.default = "browser"

# ------------------------------------------------------------------------------
# Streamlit-Authenticator Login Setup (For internal staff only)
# ------------------------------------------------------------------------------

# Define internal credentials (for demonstration purposes only)
names = ["Staff One", "Staff Two"]
usernames = ["staff1", "staff2"]
passwords = ["password1", "password2"]

# Generate hashed passwords (this only needs to be done once)
hashed_passwords = stauth.Hasher(passwords).generate()

credentials = {
    "usernames": {
        "staff1": {"name": names[0], "password": hashed_passwords[0]},
        "staff2": {"name": names[1], "password": hashed_passwords[1]},
    }
}

# Create the authenticator object.
authenticator = stauth.Authenticate(
    credentials,
    "some_cookie_name",        # a unique cookie name
    "some_signature_key",      # a unique signature key
    cookie_expiry_days=30
)

# Render the login widget
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.title(f"Welcome, {name}")
    authenticator.logout("Logout", "sidebar")
    
    # ------------------------------------------------------------------------------
    # Application Code (Accessible only after successful login)
    # ------------------------------------------------------------------------------

    def print_expected_csv_format():
        """Displays the expected CSV format for the user."""
        st.markdown(
            """
            ## 🔹 Expected CSV Column Order
            | # | Column |
            |---|------------------------------|
            | 1 | Item ID |
            | 2 | Impressions (Impr.) |
            | 3 | Clicks |
            | 4 | Click-Through Rate (CTR) |
            | 5 | Conversions |
            | 6 | Conversion Value (Conv. value) |
            | 7 | Cost |
            | 8 | Conversion Value / Cost (ROAS) |
            | 9 | Search Impression Share |
            
            **Ensure that your CSV file follows this format before uploading.**
            """
        )

    def detect_header_row(file_path: str) -> int:
        """Detects the correct header row by scanning the first few lines of the CSV."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if "Item ID" in line and "Impr." in line:
                        return i  # This row is the actual header
        except Exception as e:
            logging.error(f"Error detecting header row: {e}")
        return 0  # Default to first row if no match is found

    def process_large_csv(file_path: str, chunk_size: int = 100000) -> Tuple[Dict[str, float], Dict]:
        """
        Processes large CSV files in chunks, automatically detecting the header row,
        computes overall metrics, and performs a Pareto analysis of SKUs.
        
        Returns:
            insights: A dictionary containing overall metrics.
            sku_sales: A dictionary mapping SKU to its total sales (conversion value).
        """
        
        # Detect the correct header row
        header_row = detect_header_row(file_path)
        
        # Initialise totals
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_conversion_value = 0
        total_cost = 0
        total_search_impr_share = 0
        valid_search_impr_count = 0
        
        # Dictionary to accumulate sales (conversion value) by SKU
        sku_sales = defaultdict(float)
        
        try:
            for chunk in pd.read_csv(
                file_path, 
                chunksize=chunk_size, 
                encoding="utf-8", 
                on_bad_lines="skip", 
                skiprows=header_row
            ):
                # Normalise column names
                chunk.columns = chunk.columns.str.strip().str.lower()
                
                # Verify if required columns exist
                required_columns = ["impr.", "clicks", "conversions", "conv. value", "cost"]
                missing_columns = [col for col in required_columns if col not in chunk.columns]
                if missing_columns:
                    st.error(f"❌ Missing expected columns: {', '.join(missing_columns)}")
                    st.write("🔍 Detected Columns in Uploaded File:", list(chunk.columns))
                    return {}, {}
                
                # Clean and convert numeric columns in a vectorised manner
                for col in required_columns:
                    chunk[col] = pd.to_numeric(chunk[col].astype(str).str.replace(",", ""), errors='coerce').fillna(0)
                
                # Calculate ROAS using vectorised operations
                chunk["roas"] = chunk["conv. value"] / chunk["cost"]
                chunk.loc[chunk["cost"] <= 0, "roas"] = 0
                
                # Process Search Impression Share if present
                if "search impr. share" in chunk.columns:
                    chunk["search impr. share"] = pd.to_numeric(
                        chunk["search impr. share"].astype(str).str.replace("%", "").replace("--", ""),
                        errors='coerce'
                    )
                else:
                    chunk["search impr. share"] = pd.NA
                
                # Aggregate overall metrics
                total_impressions += chunk["impr."].sum()
                total_clicks += chunk["clicks"].sum()
                total_conversions += chunk["conversions"].sum()
                total_conversion_value += chunk["conv. value"].sum()
                total_cost += chunk["cost"].sum()
                
                valid_search_chunk = chunk["search impr. share"].dropna()
                total_search_impr_share += valid_search_chunk.sum()
                valid_search_impr_count += valid_search_chunk.count()
                
                # Update SKU sales if "item id" exists
                if "item id" in chunk.columns:
                    sku_group = chunk.groupby("item id")["conv. value"].sum()
                    for sku, sale in sku_group.items():
                        sku_sales[sku] += sale
                else:
                    logging.warning("Column 'item id' not found in the CSV chunk.")
            
            # Compute Pareto metric: SKUs driving 80% of total sales
            pareto_threshold = 0.8 * total_conversion_value if total_conversion_value else 0
            sorted_skus = sorted(sku_sales.items(), key=lambda x: x[1], reverse=True)
            accumulated_sales = 0
            sku_count_for_pareto = 0
            
            for sku, sale in sorted_skus:
                accumulated_sales += sale
                sku_count_for_pareto += 1
                if accumulated_sales >= pareto_threshold:
                    break
            
            total_unique_skus = len(sku_sales) if sku_sales else 0
            pareto_percentage = (sku_count_for_pareto / total_unique_skus * 100) if total_unique_skus else 0
            
            # Compute final metrics
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
        except Exception as e:
            st.error(f"Error processing file: {e}")
            logging.error(f"Error processing CSV file: {e}")
            return {}, {}

    def create_metrics_bar_chart(insights: Dict[str, float]) -> go.Figure:
        """Creates a Plotly bar chart for the overall campaign metrics (excluding Pareto metrics)."""
        metrics = {
            "Total Impressions": insights.get("Total Impressions", 0),
            "Total Clicks": insights.get("Total Clicks", 0),
            "Total Conversions": insights.get("Total Conversions", 0),
            "Total Conversion Value": insights.get("Total Conversion Value", 0),
            "Total Cost": insights.get("Total Cost", 0)
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color='indianred'
        )])
        
        fig.update_layout(
            title="Campaign Performance Metrics",
            xaxis_title="Metric",
            yaxis_title="Value",
            template="plotly_white"
        )
        
        return fig

    def create_pareto_chart(sku_sales: dict, total_conversion_value: float) -> go.Figure:
        """
        Creates a Pareto chart displaying each SKU's sales (as bars) along with a line
        representing the cumulative percentage of total sales.
        """
        # Convert sku_sales dict to a DataFrame
        df = pd.DataFrame(list(sku_sales.items()), columns=["SKU", "Sales"])
        df = df.sort_values(by="Sales", ascending=False)
        df["Cumulative Sales"] = df["Sales"].cumsum()
        df["Cumulative Percentage"] = df["Cumulative Sales"] / total_conversion_value

        # Determine how many SKUs drive 80% of total sales
        sku_count_80 = (df["Cumulative Percentage"] < 0.8).sum() + 1

        fig = go.Figure()
        
        # Bar chart for individual SKU sales
        fig.add_trace(go.Bar(
            x=df["SKU"],
            y=df["Sales"],
            name="Sales",
            marker_color='lightskyblue'
        ))
        
        # Line chart for cumulative percentage
        fig.add_trace(go.Scatter(
            x=df["SKU"],
            y=df["Cumulative Percentage"],
            mode='lines+markers',
            name="Cumulative %",
            marker_color='indianred',
            yaxis="y2"
        ))
        
        # Dual y-axes configuration
        fig.update_layout(
            title="Pareto Analysis: SKU Contribution to Sales",
            xaxis_title="SKU",
            yaxis=dict(
                title="Sales",
                showgrid=False,
                zeroline=True
            ),
            yaxis2=dict(
                title="Cumulative Percentage",
                overlaying="y",
                side="right",
                tickformat=".0%",
                showgrid=False,
                zeroline=True,
                range=[0, 1]
            ),
            legend=dict(x=0.01, y=0.99),
            bargap=0.2,
            template="plotly_white"
        )
        
        # Add a horizontal line at 80% on the cumulative axis
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(df["SKU"]) - 0.5,
            y0=0.8,
            y1=0.8,
            yref="y2",
            line=dict(color="Green", dash="dash")
        )
        
        # Annotate the number of SKUs that drive 80% of sales
        fig.add_annotation(
            x=0.5,
            y=0.85,
            xref="paper",
            yref="paper",
            text=f"{sku_count_80} SKUs drive 80% of sales",
            showarrow=False,
            font=dict(color="Green", size=12)
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig

    def run_web_ui():
        """Creates a web-based interface for uploading a CSV file and processing it in chunks."""
        st.title("📊 PMax Audit Dashboard")
        st.write("Analyse your Performance Max campaign data efficiently without file size limits.")
        print_expected_csv_format()
        
        uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv", key="file_uploader")
        
        if uploaded_file:
            with st.spinner("Processing file..."):
                try:
                    # Use a temporary file for handling the uploaded CSV
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_file_path = tmp_file.name
                    
                    # Process the file in chunks and retrieve insights and SKU sales data
                    insights, sku_sales = process_large_csv(tmp_file_path)
                    
                    if insights:
                        st.subheader("📊 Summary Metrics")
                        summary_df = pd.DataFrame({
                            "Metric": list(insights.keys()),
                            "Value": list(insights.values())
                        })
                        st.table(summary_df)
                        
                        # Display overall metrics chart
                        st.subheader("📈 Visual Overview")
                        metrics_fig = create_metrics_bar_chart(insights)
                        st.plotly_chart(metrics_fig, use_container_width=True)
                        
                        # Display Pareto Analysis chart if SKU sales data exists
                        if sku_sales and insights.get("Total Conversion Value", 0) > 0:
                            st.subheader("📉 Pareto Analysis")
                            pareto_fig = create_pareto_chart(sku_sales, insights["Total Conversion Value"])
                            st.plotly_chart(pareto_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    logging.error(f"Unexpected error in run_web_ui: {e}")

    if __name__ == "__main__":
        # Clear cache to prevent duplicate elements
        st.cache_data.clear()  
        run_web_ui()
        
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
