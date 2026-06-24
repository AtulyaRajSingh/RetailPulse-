from __future__ import annotations

import pandas as pd

SCHEMAS: dict[str, dict[str, str]] = {
    "sales": {
        "date": "datetime64[ns]",
        "product_id": "object",
        "quantity_sold": "number",
        "revenue": "number",
    },
    "customers": {
        "customer_id": "object",
        "signup_date": "datetime64[ns]",
        "region": "object",
    },
    "inventory": {
        "product_id": "object",
        "stock_on_hand": "number",
        "lead_time_days": "number",
    },
    "transactions": {
        "transaction_id": "object",
        "date": "datetime64[ns]",
        "customer_id": "object",
        "product_id": "object",
        "quantity": "number",
        "revenue": "number",
    },
}


def validate_dataset(name: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        raise ValueError(f"{name} dataset is empty")
    required = SCHEMAS[name]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} dataset missing required columns: {missing}")

    for column, expected in required.items():
        series = frame[column]
        if expected == "number" and not pd.api.types.is_numeric_dtype(series):
            coerced = pd.to_numeric(series, errors="coerce")
            if coerced.notna().sum() == 0:
                raise ValueError(f"{name}.{column} must be numeric")
        if expected.startswith("datetime") and not pd.api.types.is_datetime64_any_dtype(series):
            converted = pd.to_datetime(series, errors="coerce")
            if converted.notna().sum() == 0:
                raise ValueError(f"{name}.{column} must be parseable as dates")


def validation_summary(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, frame in datasets.items():
        required = set(SCHEMAS.get(name, {}))
        rows.append(
            {
                "dataset": name,
                "rows": len(frame),
                "columns": len(frame.columns),
                "missing_required": ", ".join(sorted(required - set(frame.columns))) or "none",
                "duplicate_rows": int(frame.duplicated().sum()),
                "missing_cells": int(frame.isna().sum().sum()),
            }
        )
    return pd.DataFrame(rows)
