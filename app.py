from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.forecasting.ensemble_forecast import ensemble_forecast
from src.inventory.inventory_optimizer import optimize_inventory
from src.segmentation.segment_customers import segment_from_transactions
from src.utils.reports import build_pdf_report
from src.utils.streamlit_helpers import category_chart, configure_page, kpi_row, revenue_chart, upload_data_sidebar
from src.utils.design_tokens import get_tokens
import streamlit as st
import plotly.express as px

configure_page("Executive Dashboard")
data = upload_data_sidebar()
sales = data["sales"].copy()
transactions = data["transactions"].copy()
inventory = data["inventory"].copy()

# Title moved to the sticky header in `configure_page()`; avoid duplicate page title/subtitle here.

total_revenue = sales["revenue"].sum()
total_units = sales["quantity_sold"].sum()
customers = transactions["customer_id"].nunique()
stock_alerts = optimize_inventory(sales, inventory)
kpi_row(
    [
        ("Revenue", f"${total_revenue:,.0f}", None),
        ("Units Sold", f"{total_units:,.0f}", None),
        ("Active Customers", f"{customers:,}", None),
        ("Inventory Alerts", int((stock_alerts["alert"] != "Healthy").sum()), None),
    ]
)

left, right = st.columns([1.45, 1])
with left:
    st.plotly_chart(revenue_chart(sales), use_container_width=True)
with right:
    st.plotly_chart(category_chart(sales), use_container_width=True)

forecast = ensemble_forecast(sales, periods=30)
segments = segment_from_transactions(transactions)

# get current theme tokens for chart styling
tokens = get_tokens("dark" if st.session_state.get("theme", "Dark") == "Dark" else "light")

# Forecast chart: explicit template and styling to ensure visibility
try:
    fig_forecast = px.line(forecast, x="date", y="ensemble_yhat", title="Expected Unit Demand", template=("plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"), color_discrete_sequence=[tokens["accent"]])
    fig_forecast.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=tokens["text"], height=340)
except Exception:
    fig_forecast = None

# Segments pie chart: explicit styling
try:
    counts = segments["segment"].value_counts().reset_index()
    counts.columns = ["segment", "customers"]
    fig_segments = px.pie(counts, names="segment", values="customers", hole=0.45, title="Customer Segments", template=("plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"))
    fig_segments.update_traces(textposition='inside', textinfo='percent+label')
    fig_segments.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=tokens["text"], height=340)
except Exception:
    fig_segments = None

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="section-title">30-Day Demand Forecast</div>', unsafe_allow_html=True)
    if fig_forecast is not None:
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.write("Forecast chart unavailable")
with col2:
    st.markdown('<div class="section-title">Customer Portfolio</div>', unsafe_allow_html=True)
    if fig_segments is not None:
        st.plotly_chart(fig_segments, use_container_width=True)
    else:
        st.write("Segments chart unavailable")

report_path = build_pdf_report(
    "RetailPulse Executive Report",
    {
        "Sales Snapshot": sales.head(20),
        "Forecast": forecast,
        "Inventory Recommendations": stock_alerts.head(20),
    },
    "reports/executive_report.pdf",
)
with open(report_path, "rb") as report:
    st.download_button("Download executive PDF", report, file_name="retailpulse_executive_report.pdf", mime="application/pdf")
