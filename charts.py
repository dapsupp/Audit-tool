import plotly.graph_objects as go

def plot_chart(df, metric, title=None, x_label="Item ID", y_label=None):
    """Generate a Plotly bar chart for a given metric."""
    if 'item id' not in df.columns or metric not in df.columns:
        raise ValueError(f"DataFrame must contain 'item id' and '{metric}' columns.")

    if title is None:
        title = f"Performance Chart: {metric}"
    if y_label is None:
        y_label = metric

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['item id'], y=df[metric], name=metric))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template="plotly_white"
    )
    return fig
