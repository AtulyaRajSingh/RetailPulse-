from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger(__name__)


NUMERIC_BY_DATASET = {
    "sales": ["quantity_sold", "revenue", "orders"],
    "inventory": ["stock_on_hand", "lead_time_days", "holding_cost", "ordering_cost", "service_level"],
    "transactions": ["quantity", "unit_price", "discount", "revenue"],
}


def _cap_outliers(series: pd.Series, factor: float = 1.5) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return values
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return values.clip(lower=lower, upper=upper)


def clean_dataset(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    cleaned.columns = [str(col).strip().lower().replace(" ", "_") for col in cleaned.columns]
    before = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    logger.info("Removed %s duplicate rows from %s", before - len(cleaned), name)

    for column in cleaned.columns:
        if "date" in column:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    numeric_columns = [col for col in NUMERIC_BY_DATASET.get(name, []) if col in cleaned.columns]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = cleaned[column].fillna(cleaned[column].median())
        cleaned[column] = _cap_outliers(cleaned[column])
        cleaned[column] = np.where(cleaned[column] < 0, 0, cleaned[column])

    object_columns = cleaned.select_dtypes(include=["object"]).columns
    for column in object_columns:
        cleaned[column] = cleaned[column].fillna("Unknown").astype(str).str.strip()

    date_columns = cleaned.select_dtypes(include=["datetime64[ns]"]).columns
    for column in date_columns:
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())

    return cleaned


def detect_outliers(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        rows.append(
            {
                "column": column,
                "lower_bound": lower,
                "upper_bound": upper,
                "outliers": int(((values < lower) | (values > upper)).sum()),
            }
        )
    return pd.DataFrame(rows)
