from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

from src.etl.data_cleaner import clean_dataset
from src.etl.data_validator import validate_dataset
from src.utils.logging import get_logger

logger = get_logger(__name__)


DATASET_NAMES = {"sales", "customers", "inventory", "transactions"}


def load_csv(path_or_buffer: str | Path | BinaryIO, parse_dates: list[str] | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path_or_buffer, parse_dates=parse_dates)
    frame.columns = [str(col).strip().lower().replace(" ", "_") for col in frame.columns]
    logger.info("Loaded dataset with %s rows and %s columns", len(frame), len(frame.columns))
    return frame


def load_dataset(name: str, path_or_buffer: str | Path | BinaryIO) -> pd.DataFrame:
    normalized = name.lower().replace(".csv", "")
    if normalized not in DATASET_NAMES:
        raise ValueError(f"Unsupported dataset '{name}'. Expected one of {sorted(DATASET_NAMES)}")
    date_columns = {
        "sales": ["date"],
        "customers": ["signup_date"],
        "transactions": ["date"],
        "inventory": [],
    }[normalized]
    frame = load_csv(path_or_buffer, parse_dates=date_columns)
    validate_dataset(normalized, frame)
    return clean_dataset(normalized, frame)


def load_retail_datasets(base_path: str | Path) -> dict[str, pd.DataFrame]:
    base = Path(base_path)
    datasets = {}
    for name in sorted(DATASET_NAMES):
        path = base / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing required dataset: {path}")
        datasets[name] = load_dataset(name, path)
    return datasets


def save_processed_datasets(datasets: dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in datasets.items():
        frame.to_parquet(output / f"{name}.parquet", index=False)
        frame.to_csv(output / f"{name}.csv", index=False)
        logger.info("Saved processed %s dataset to %s", name, output)
