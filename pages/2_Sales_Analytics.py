from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.utils.streamlit_helpers import (
    category_chart,
    configure_page,
    download_frame,
    kpi_row,
    revenue_chart,
    sales_filters,
    upload_data_sidebar,
)

configure_page("Sales Analytics")
data = upload_data_sidebar()
sales = sales_filters(data["sales"])

st.title("Sales Analytics")
kpi_row(
    [
        ("Revenue", f"${sales['revenue'].sum():,.0f}", None),
        ("Units", f"{sales['quantity_sold'].sum():,.0f}", None),
        ("Avg Order Revenue", f"${sales['revenue'].mean():,.2f}", None),
        ("Products", sales["product_id"].nunique(), None),
    ]
)

left, right = st.columns(2)
left.plotly_chart(revenue_chart(sales), use_container_width=True)
right.plotly_chart(category_chart(sales), use_container_width=True)

product = (
    sales.groupby("product_id", as_index=False)
    .agg(revenue=("revenue", "sum"), units=("quantity_sold", "sum"))
    .sort_values("revenue", ascending=False)
)
st.plotly_chart(
    px.bar(product, x="product_id", y="revenue", color="units", title="Product Revenue Ranking"),
    use_container_width=True,
)
st.dataframe(product, use_container_width=True, hide_index=True)
download_frame("Download sales analytics", product, "sales_analytics.csv")
