from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from src.database.models import Customer, Forecast, Inventory, Prediction, Sale


def upsert_dataframe(session: Session, frame: pd.DataFrame, model: type) -> int:
    records = frame.to_dict(orient="records")
    for record in records:
        session.merge(model(**record))
    return len(records)


def store_sales(session: Session, sales: pd.DataFrame) -> int:
    cols = ["date", "product_id", "quantity_sold", "revenue"]
    return upsert_dataframe(session, sales[cols], Sale)


def store_customers(session: Session, customers: pd.DataFrame) -> int:
    cols = ["customer_id", "name", "email", "signup_date", "region", "loyalty_tier"]
    return upsert_dataframe(session, customers[cols], Customer)


def store_inventory(session: Session, inventory: pd.DataFrame) -> int:
    cols = ["product_id", "product_name", "category", "unit_price", "stock_on_hand", "lead_time_days"]
    return upsert_dataframe(session, inventory[cols], Inventory)


def store_forecasts(session: Session, forecasts: pd.DataFrame, product_id: str = "ALL", model_name: str = "ensemble") -> int:
    frame = forecasts.rename(columns={"ensemble_yhat": "forecast_quantity"}).copy()
    frame["product_id"] = product_id
    frame["model_name"] = model_name
    return upsert_dataframe(session, frame[["product_id", "date", "forecast_quantity", "model_name"]], Forecast)


def store_predictions(session: Session, scored: pd.DataFrame, prediction_type: str = "churn") -> int:
    frame = pd.DataFrame(
        {
            "customer_id": scored["customer_id"],
            "prediction_type": prediction_type,
            "score": scored["churn_probability"],
            "label": scored["risk_band"],
        }
    )
    return upsert_dataframe(session, frame, Prediction)
