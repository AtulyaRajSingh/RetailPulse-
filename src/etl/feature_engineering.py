from __future__ import annotations

import pandas as pd

try:
    import holidays
except Exception:  # pragma: no cover - optional dependency fallback
    holidays = None


def create_rfm_features(transactions: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    tx = transactions.copy()
    tx["date"] = pd.to_datetime(tx["date"])
    if reference_date is None:
        reference_date = tx["date"].max() + pd.Timedelta(days=1)
    rfm = (
        tx.groupby("customer_id")
        .agg(
            recency=("date", lambda dates: (reference_date - dates.max()).days),
            frequency=("transaction_id", "nunique"),
            monetary=("revenue", "sum"),
            avg_order_value=("revenue", "mean"),
            last_purchase_date=("date", "max"),
        )
        .reset_index()
    )
    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["avg_order_value"] = rfm["avg_order_value"].round(2)
    return rfm


def create_time_features(frame: pd.DataFrame, date_col: str = "date", country: str = "US") -> pd.DataFrame:
    enriched = frame.copy()
    dates = pd.to_datetime(enriched[date_col])
    enriched["month"] = dates.dt.month
    enriched["week"] = dates.dt.isocalendar().week.astype(int)
    enriched["quarter"] = dates.dt.quarter
    enriched["day_of_week"] = dates.dt.dayofweek
    enriched["is_weekend"] = dates.dt.dayofweek.isin([5, 6]).astype(int)
    if holidays is not None:
        holiday_calendar = holidays.country_holidays(country)
        enriched["is_holiday"] = dates.dt.date.map(lambda day: int(day in holiday_calendar))
    else:
        enriched["is_holiday"] = 0
    return enriched


def create_lag_features(
    sales: pd.DataFrame,
    group_col: str = "product_id",
    date_col: str = "date",
    target_col: str = "quantity_sold",
) -> pd.DataFrame:
    frame = sales.copy()
    frame[date_col] = pd.to_datetime(frame[date_col])
    frame = frame.sort_values([group_col, date_col])
    grouped = frame.groupby(group_col, group_keys=False)[target_col]
    frame["lag_1"] = grouped.shift(1)
    frame["lag_7"] = grouped.shift(7)
    frame["rolling_mean_7"] = grouped.shift(1).rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    frame["rolling_mean_30"] = grouped.shift(1).rolling(30, min_periods=1).mean().reset_index(level=0, drop=True)
    frame["moving_average_14"] = grouped.shift(1).rolling(14, min_periods=1).mean().reset_index(level=0, drop=True)
    for column in ["lag_1", "lag_7", "rolling_mean_7", "rolling_mean_30", "moving_average_14"]:
        frame[column] = frame[column].fillna(frame.groupby(group_col)[target_col].transform("mean"))
    return create_time_features(frame, date_col=date_col)


def build_modeling_table(sales: pd.DataFrame, inventory: pd.DataFrame | None = None) -> pd.DataFrame:
    features = create_lag_features(sales)
    if inventory is not None:
        inventory_cols = [
            col for col in ["product_id", "stock_on_hand", "lead_time_days", "unit_price", "category"] if col in inventory.columns
        ]
        features = features.merge(inventory[inventory_cols], on="product_id", how="left")
    return features
