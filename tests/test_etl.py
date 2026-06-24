from __future__ import annotations

from src.etl.data_validator import validation_summary
from src.etl.feature_engineering import create_lag_features, create_rfm_features
from src.utils.sample_data import generate_sample_data


def test_sample_data_validates_and_features(tmp_path):
    data = generate_sample_data(tmp_path, n_customers=30, days=45)
    summary = validation_summary(data)
    assert summary["missing_required"].eq("none").all()
    rfm = create_rfm_features(data["transactions"])
    assert {"recency", "frequency", "monetary"}.issubset(rfm.columns)
    lagged = create_lag_features(data["sales"])
    assert {"rolling_mean_7", "rolling_mean_30", "month", "week", "quarter"}.issubset(lagged.columns)
