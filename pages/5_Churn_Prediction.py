from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.churn.churn_model import train_and_score_churn
from src.churn.feature_importance import get_feature_importance
from src.churn.shap_analysis import customer_reason_codes, shap_summary
from src.utils.streamlit_helpers import configure_page, download_frame, kpi_row, upload_data_sidebar

configure_page("Churn Prediction")
data = upload_data_sidebar()

st.title("Churn Prediction")
model_name = st.selectbox("Model", ["random_forest", "logistic_regression", "xgboost"])
scored, artifacts = train_and_score_churn(data["transactions"], model_name=model_name)
high_risk = scored[scored["risk_band"] == "High"]

kpi_row(
    [
        ("ROC AUC", f"{artifacts.metrics['roc_auc']:.3f}", None),
        ("High Risk Customers", len(high_risk), None),
        ("Avg Churn Probability", f"{scored['churn_probability'].mean():.1%}", None),
        ("Customers Scored", f"{len(scored):,}", None),
    ]
)

left, right = st.columns(2)
left.plotly_chart(
    px.histogram(scored, x="churn_probability", color="risk_band", title="Churn Probability Distribution"),
    use_container_width=True,
)
right.plotly_chart(
    px.bar(get_feature_importance(artifacts), x="feature", y="importance", title="Feature Importance"),
    use_container_width=True,
)

st.markdown('<div class="section-title">SHAP / Explainability Summary</div>', unsafe_allow_html=True)
st.dataframe(shap_summary(artifacts), use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Top At-Risk Customers</div>', unsafe_allow_html=True)
st.dataframe(customer_reason_codes(scored).head(25), use_container_width=True, hide_index=True)
download_frame("Download churn scores", scored, "churn_scores.csv")
