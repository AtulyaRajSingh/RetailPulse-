from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def rfm_scatter(segmented: pd.DataFrame) -> go.Figure:
    return px.scatter(
        segmented,
        x="recency",
        y="monetary",
        size="frequency",
        color="segment",
        hover_data=["customer_id", "avg_order_value", "rfm_score"],
        title="Customer Segments by Recency and Monetary Value",
    )


def segment_distribution(segmented: pd.DataFrame) -> go.Figure:
    counts = segmented["segment"].value_counts().reset_index()
    counts.columns = ["segment", "customers"]
    return px.bar(counts, x="segment", y="customers", color="segment", title="Segment Distribution")


def segment_value_matrix(segmented: pd.DataFrame) -> go.Figure:
    matrix = (
        segmented.groupby("segment", as_index=False)
        .agg(customers=("customer_id", "count"), avg_monetary=("monetary", "mean"), avg_frequency=("frequency", "mean"))
        .round(2)
    )
    return px.scatter(
        matrix,
        x="avg_frequency",
        y="avg_monetary",
        size="customers",
        color="segment",
        title="Segment Value Matrix",
    )
