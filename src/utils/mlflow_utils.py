from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from src.utils.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


@contextmanager
def mlflow_run(experiment_name: str, run_name: str) -> Iterator[object | None]:
    try:
        import mlflow

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run(run_name=run_name) as run:
            yield mlflow
            logger.info("Logged MLflow run %s", run.info.run_id)
    except Exception as exc:
        logger.warning("MLflow unavailable; continuing without tracking: %s", exc)
        yield None


def log_model_metrics(experiment_name: str, run_name: str, params: dict, metrics: dict, model: object | None = None) -> None:
    with mlflow_run(experiment_name, run_name) as mlflow:
        if mlflow is None:
            return
        mlflow.log_params(params)
        mlflow.log_metrics({k: float(v) for k, v in metrics.items() if v is not None})
        if model is not None:
            try:
                mlflow.sklearn.log_model(model, artifact_path="model")
            except Exception:
                logger.exception("Failed to log model artifact")
