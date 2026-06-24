from __future__ import annotations

import streamlit as st

from src.segmentation.cluster_visualizations import rfm_scatter, segment_distribution, segment_value_matrix
from src.segmentation.segment_customers import run_dbscan_segmentation, segment_from_transactions
from src.segmentation.segment_interpretation import summarize_segments, top_segment_actions
from src.utils.streamlit_helpers import configure_page, download_frame, upload_data_sidebar

configure_page("Customer Segmentation")
data = upload_data_sidebar()
transactions = data["transactions"]

st.title("Customer Segmentation")
method = st.radio("Clustering method", ["K-Means + RFM Labels", "DBSCAN + RFM Labels"], horizontal=True)
segmented = segment_from_transactions(transactions)
if method.startswith("DBSCAN"):
    segmented, _ = run_dbscan_segmentation(
        segmented[["customer_id", "recency", "frequency", "monetary", "avg_order_value", "last_purchase_date"]]
    )

summary = summarize_segments(segmented)
col1, col2 = st.columns(2)
col1.plotly_chart(segment_distribution(segmented), use_container_width=True)
col2.plotly_chart(segment_value_matrix(segmented), use_container_width=True)
st.plotly_chart(rfm_scatter(segmented), use_container_width=True)
st.dataframe(summary, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Recommended Customer Actions</div>', unsafe_allow_html=True)
st.dataframe(top_segment_actions(segmented), use_container_width=True, hide_index=True)
download_frame("Download segments", segmented, "customer_segments.csv")
