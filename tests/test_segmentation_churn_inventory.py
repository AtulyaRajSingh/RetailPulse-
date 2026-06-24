from __future__ import annotations

from src.churn.churn_model import train_and_score_churn
from src.inventory.inventory_optimizer import optimize_inventory
from src.segmentation.segment_customers import segment_from_transactions
from src.utils.sample_data import generate_sample_data


def test_segmentation_churn_inventory_pipeline(tmp_path):
    data = generate_sample_data(tmp_path, n_customers=50, days=90)
    segments = segment_from_transactions(data["transactions"])
    assert "segment" in segments
    scored, artifacts = train_and_score_churn(data["transactions"])
    assert "churn_probability" in scored
    assert "roc_auc" in artifacts.metrics
    inventory = optimize_inventory(data["sales"], data["inventory"])
    assert {"safety_stock", "reorder_point", "eoq", "alert"}.issubset(inventory.columns)
