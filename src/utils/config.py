from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "RetailPulse")
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + str(BASE_DIR / "retailpulse.db"),
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", str(BASE_DIR / "mlruns"))
    model_dir: Path = BASE_DIR / os.getenv("MODEL_DIR", "models")
    report_dir: Path = BASE_DIR / os.getenv("REPORT_DIR", "reports")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "9000"))


settings = Settings()


def ensure_runtime_dirs() -> None:
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
