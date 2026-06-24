from __future__ import annotations

from src.forecasting.ensemble_forecast import ensemble_forecast
from src.forecasting.forecast_evaluation import evaluate_forecast
from src.utils.sample_data import generate_sample_data


def test_ensemble_forecast_outputs_requested_horizon(tmp_path):
    data = generate_sample_data(tmp_path, n_customers=25, days=60)
    forecast = ensemble_forecast(data["sales"], periods=10)
    assert len(forecast) == 10
    assert (forecast["ensemble_yhat"] >= 0).all()


def test_forecast_metrics_are_numeric():
    metrics = evaluate_forecast([10, 20, 30], [12, 18, 33])
    assert set(metrics) == {"MAE", "RMSE", "MAPE"}
    assert all(value >= 0 for value in metrics.values())
