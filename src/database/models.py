from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    product_id: Mapped[str] = mapped_column(String(64), index=True)
    quantity_sold: Mapped[float] = mapped_column(Float)
    revenue: Mapped[float] = mapped_column(Float)


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), index=True)
    signup_date: Mapped[Date] = mapped_column(Date)
    region: Mapped[str] = mapped_column(String(64))
    loyalty_tier: Mapped[str] = mapped_column(String(64), default="Bronze")


class Inventory(Base):
    __tablename__ = "inventory"

    product_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(128))
    unit_price: Mapped[float] = mapped_column(Float)
    stock_on_hand: Mapped[int] = mapped_column(Integer)
    lead_time_days: Mapped[int] = mapped_column(Integer)


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String(64), index=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    forecast_quantity: Mapped[float] = mapped_column(Float)
    model_name: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    prediction_type: Mapped[str] = mapped_column(String(64), index=True)
    score: Mapped[float] = mapped_column(Float)
    label: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
