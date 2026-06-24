from __future__ import annotations

import streamlit as st

from src.churn.churn_model import train_and_score_churn
from src.drift.drift_detector import drift_summary, generate_drift_report
from src.forecasting.ensemble_forecast import ensemble_forecast
from src.inventory.inventory_optimizer import optimize_inventory
from src.segmentation.segment_customers import segment_from_transactions
from src.utils.config import BASE_DIR
from src.utils.reports import build_pdf_report
from src.utils.streamlit_helpers import configure_page, download_frame, upload_data_sidebar

configure_page("Reports")
data = upload_data_sidebar()

st.title("Reports")
forecast = ensemble_forecast(data["sales"], periods=30)
segments = segment_from_transactions(data["transactions"])
churn, _ = train_and_score_churn(data["transactions"])
inventory = optimize_inventory(data["sales"], data["inventory"])

tabs = st.tabs(["Forecast", "Segments", "Churn", "Inventory", "Drift"])
tabs[0].dataframe(forecast, use_container_width=True, hide_index=True)
tabs[1].dataframe(segments, use_container_width=True, hide_index=True)
tabs[2].dataframe(churn, use_container_width=True, hide_index=True)
tabs[3].dataframe(inventory, use_container_width=True, hide_index=True)

sales = data["sales"].copy()
mid = max(1, len(sales) // 2)
drift = drift_summary(sales.iloc[:mid], sales.iloc[mid:])
tabs[4].dataframe(drift, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate PDF report", type="primary", use_container_width=True):
        path = build_pdf_report(
            "RetailPulse Analytics Report",
            {"Forecast": forecast, "Segments": segments, "Churn": churn.head(25), "Inventory": inventory},
            BASE_DIR / "reports" / "analytics_report.pdf",
        )
        st.success(f"Generated {path}")
with col2:
    if st.button("Generate drift HTML", use_container_width=True):
        path = generate_drift_report(sales.iloc[:mid], sales.iloc[mid:], BASE_DIR / "reports" / "drift_report.html")
        st.success(f"Generated {path}")

download_frame("Download forecast CSV", forecast, "forecast_report.csv")
