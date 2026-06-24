from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.forecasting.ensemble_forecast import ensemble_forecast
from src.forecasting.prophet_model import ProphetDemandModel
from src.utils.streamlit_helpers import configure_page, download_frame, upload_data_sidebar

configure_page("Demand Forecasting")
data = upload_data_sidebar()
sales = data["sales"]

st.title("Demand Forecasting")
product_options = ["All Products"] + sorted(sales["product_id"].unique())
selected = st.selectbox("Product", product_options)
periods = st.slider("Forecast horizon", 7, 90, 30)
product_id = None if selected == "All Products" else selected

forecast = ensemble_forecast(sales, periods=periods, product_id=product_id)
history = ProphetDemandModel.prepare_daily_series(sales, product_id)

fig = go.Figure()
fig.add_trace(go.Scatter(x=history["ds"], y=history["y"], name="Actual"))
fig.add_trace(go.Scatter(x=forecast["date"], y=forecast["ensemble_yhat"], name="Ensemble Forecast"))
fig.add_trace(go.Scatter(x=forecast["date"], y=forecast["yhat"], name="Prophet/Fallback"))
fig.add_trace(go.Scatter(x=forecast["date"], y=forecast["lstm_yhat"], name="LSTM/Fallback"))
fig.update_layout(title="Demand Forecast Comparison", xaxis_title="Date", yaxis_title="Units")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(forecast, use_container_width=True, hide_index=True)
download_frame("Download forecast", forecast, "demand_forecast.csv")
