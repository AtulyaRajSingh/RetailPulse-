from __future__ import annotations

import streamlit as st

from src.inventory.inventory_dashboard import inventory_alert_chart, stock_vs_reorder_chart
from src.inventory.inventory_optimizer import optimize_inventory
from src.inventory.reorder_engine import generate_reorder_suggestions
from src.utils.streamlit_helpers import configure_page, download_frame, kpi_row, upload_data_sidebar

configure_page("Inventory Optimization")
data = upload_data_sidebar()
optimized = optimize_inventory(data["sales"], data["inventory"])
suggestions = generate_reorder_suggestions(data["sales"], data["inventory"])

st.title("Inventory Optimization")
kpi_row(
    [
        ("Low Stock", int((optimized["alert"] == "Low-stock alert").sum()), None),
        ("Overstock", int((optimized["alert"] == "Overstock alert").sum()), None),
        ("Healthy SKUs", int((optimized["alert"] == "Healthy").sum()), None),
        ("Suggested Units", int(optimized["recommended_reorder_qty"].sum()), None),
    ]
)

left, right = st.columns(2)
left.plotly_chart(inventory_alert_chart(optimized), use_container_width=True)
right.plotly_chart(stock_vs_reorder_chart(optimized), use_container_width=True)
st.dataframe(suggestions, use_container_width=True, hide_index=True)
download_frame("Download inventory recommendations", optimized, "inventory_recommendations.csv")
