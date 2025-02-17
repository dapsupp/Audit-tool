import pandas as pd
import plotly.graph_objects as go
from typing import Dict

def create_metrics_bar_chart(insights: Dict[str, float]) -> go.Figure:
    """Generates a bar chart of overall campaign metrics."""
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
    Generates a Pareto chart:
      - Bars: Each SKU's sales.
      - Line: Cumulative percentage of total sales.
    """
    df = pd.DataFrame(list(sku_sales.items()), columns=["SKU", "Sales"])
    df = df.sort_values(by="Sales", ascending=False)
    df["Cumulative Sales"] = df["Sales"].cumsum()
    df["Cumulative Percentage"] = df["Cumulative Sales"] / total_conversion_value
    sku_count_80 = (df["Cumulative Percentage"] < 0.8).sum() + 1

    fig = go.Figure()
    # Bar chart for SKU sales
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
    fig.update_layout(
        title="Pareto Analysis: SKU Contribution to Sales",
        xaxis_title="SKU",
        yaxis=dict(title="Sales", showgrid=False, zeroline=True),
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
    # Horizontal line at 80% cumulative percentage
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(df["SKU"]) - 0.5,
        y0=0.8,
        y1=0.8,
        yref="y2",
        line=dict(color="Green", dash="dash")
    )
    # Annotation for the number of SKUs driving 80% of sales
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
