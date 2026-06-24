from __future__ import annotations

import pandas as pd
import streamlit as st

from src.etl.data_validator import validation_summary
from src.utils.sample_data import generate_sample_data
from src.utils.streamlit_helpers import configure_page, kpi_row, upload_data_sidebar

configure_page("Home")
data = upload_data_sidebar()

st.title("Home")
st.caption("Operational overview, data readiness, and dataset controls.")

sales = data["sales"]
transactions = data["transactions"]
inventory = data["inventory"]
date_span = pd.to_datetime(sales["date"]).agg(["min", "max"])

kpi_row(
    [
        ("Sales Rows", f"{len(sales):,}", None),
        ("Transactions", f"{len(transactions):,}", None),
        ("Products", f"{inventory['product_id'].nunique():,}", None),
        ("Date Coverage", f"{(date_span['max'] - date_span['min']).days} days", None),
    ]
)

st.markdown('<div class="section-title">Data Quality Summary</div>', unsafe_allow_html=True)
st.dataframe(validation_summary(data), use_container_width=True, hide_index=True)

if st.button("Regenerate sample datasets", type="primary"):
    st.session_state.retailpulse_data = generate_sample_data("data/sample")
    st.success("Sample datasets regenerated.")
    st.rerun()
