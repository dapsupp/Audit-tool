import plotly.graph_objects as go
import streamlit as st

def plot_chart(df, metric):
    """Generate a Plotly bar chart for a given metric."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['item id'], y=df[metric], name=metric))

    fig.update_layout(
        title=f"Performance Chart: {metric}",
        xaxis_title="Item ID",
        yaxis_title=metric,
        template="plotly_white"
    )
    return fig
