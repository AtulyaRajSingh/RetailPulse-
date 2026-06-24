from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler

from src.etl.feature_engineering import create_rfm_features

SEGMENT_ORDER = ["Lost Customers", "At-Risk Customers", "New Customers", "Regular Customers", "Loyal Customers", "VIP Customers"]


def _score_quantiles(series: pd.Series, high_is_good: bool = True) -> pd.Series:
    ranked = pd.qcut(series.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return ranked if high_is_good else 6 - ranked


def assign_business_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    segmented = rfm.copy()
    segmented["r_score"] = _score_quantiles(segmented["recency"], high_is_good=False)
    segmented["f_score"] = _score_quantiles(segmented["frequency"], high_is_good=True)
    segmented["m_score"] = _score_quantiles(segmented["monetary"], high_is_good=True)
    segmented["rfm_score"] = segmented[["r_score", "f_score", "m_score"]].sum(axis=1)
    conditions = [
        segmented["rfm_score"] >= 13,
        (segmented["r_score"] >= 4) & (segmented["f_score"] >= 4),
        (segmented["recency"] <= 30) & (segmented["frequency"] <= 2),
        segmented["rfm_score"].between(8, 10),
        (segmented["recency"] > 60) & (segmented["frequency"] >= 2),
    ]
    choices = ["VIP Customers", "Loyal Customers", "New Customers", "Regular Customers", "At-Risk Customers"]
    segmented["segment"] = np.select(conditions, choices, default="Lost Customers")
    return segmented


def run_kmeans_segmentation(rfm: pd.DataFrame, n_clusters: int = 6, random_state: int = 42) -> tuple[pd.DataFrame, KMeans]:
    features = rfm[["recency", "frequency", "monetary", "avg_order_value"]].fillna(0)
    scaler = StandardScaler()
    matrix = scaler.fit_transform(features)
    model = KMeans(n_clusters=min(n_clusters, len(rfm)), random_state=random_state, n_init=20)
    labels = model.fit_predict(matrix)
    result = assign_business_segments(rfm)
    result["kmeans_cluster"] = labels
    result.attrs["scaler"] = scaler
    return result, model


def run_dbscan_segmentation(rfm: pd.DataFrame, eps: float = 0.9, min_samples: int = 5) -> tuple[pd.DataFrame, DBSCAN]:
    features = rfm[["recency", "frequency", "monetary", "avg_order_value"]].fillna(0)
    matrix = StandardScaler().fit_transform(features)
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(matrix)
    result = assign_business_segments(rfm)
    result["dbscan_cluster"] = labels
    return result, model


def segment_from_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    rfm = create_rfm_features(transactions)
    segmented, _ = run_kmeans_segmentation(rfm)
    return segmented.sort_values(["rfm_score", "monetary"], ascending=False)
