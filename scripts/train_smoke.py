from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.churn.churn_model import train_and_score_churn
from src.forecasting.ensemble_forecast import ensemble_forecast
from src.inventory.inventory_optimizer import optimize_inventory
from src.segmentation.segment_customers import segment_from_transactions
from src.utils.sample_data import load_or_create_sample_data


def main() -> None:
    data = load_or_create_sample_data("data/sample")
    assert len(ensemble_forecast(data["sales"], periods=7)) == 7
    assert not segment_from_transactions(data["transactions"]).empty
    churn, artifacts = train_and_score_churn(data["transactions"])
    assert not churn.empty
    assert "roc_auc" in artifacts.metrics
    assert not optimize_inventory(data["sales"], data["inventory"]).empty


if __name__ == "__main__":
    main()
