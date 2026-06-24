from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except Exception:
    dag = None
    task = None


if dag is not None:

    @dag(
        dag_id="retailpulse_training_pipeline",
        start_date=datetime(2024, 1, 1),
        schedule="@daily",
        catchup=False,
        tags=["retailpulse", "mlops"],
    )
    def retailpulse_training_pipeline():
        @task
        def ingest_data() -> str:
            from src.utils.sample_data import generate_sample_data

            generate_sample_data("data/sample")
            return "data/sample"

        @task
        def feature_engineering(data_path: str) -> str:
            from src.etl.data_loader import load_retail_datasets, save_processed_datasets

            datasets = load_retail_datasets(data_path)
            save_processed_datasets(datasets, "data/processed")
            return "data/processed"

        @task
        def train_models(_: str) -> dict:
            from src.churn.churn_model import train_and_score_churn
            from src.forecasting.ensemble_forecast import ensemble_forecast
            from src.utils.sample_data import load_or_create_sample_data

            data = load_or_create_sample_data("data/sample")
            forecast = ensemble_forecast(data["sales"], periods=30)
            churn, artifacts = train_and_score_churn(data["transactions"])
            return {"forecast_rows": len(forecast), "churn_rows": len(churn), "churn_auc": artifacts.metrics["roc_auc"]}

        @task
        def evaluate_and_register(metrics: dict) -> str:
            from src.utils.mlflow_utils import log_model_metrics

            log_model_metrics("RetailPulse", "daily-training", {}, {"churn_auc": metrics["churn_auc"]})
            return "registered"

        @task
        def deploy_and_monitor(_: str) -> str:
            from src.drift.drift_detector import generate_drift_report
            from src.utils.sample_data import load_or_create_sample_data

            data = load_or_create_sample_data("data/sample")
            sales = data["sales"]
            mid = len(sales) // 2
            generate_drift_report(sales.iloc[:mid], sales.iloc[mid:], "reports/airflow_drift_report.html")
            return "complete"

        deploy_and_monitor(evaluate_and_register(train_models(feature_engineering(ingest_data()))))

    retailpulse_training_pipeline()
