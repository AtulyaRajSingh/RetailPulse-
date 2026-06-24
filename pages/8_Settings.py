from __future__ import annotations

import streamlit as st

from src.utils.config import settings
from src.utils.streamlit_helpers import configure_page, upload_data_sidebar

configure_page("Settings")
upload_data_sidebar()

st.title("Settings")
st.caption("Runtime configuration for local and deployed environments.")

st.dataframe(
    [
        {"setting": "Environment", "value": settings.environment},
        {"setting": "Database URL", "value": settings.database_url},
        {"setting": "Redis URL", "value": settings.redis_url},
        {"setting": "MLflow Tracking URI", "value": settings.mlflow_tracking_uri},
        {"setting": "Model Directory", "value": str(settings.model_dir)},
        {"setting": "Report Directory", "value": str(settings.report_dir)},
    ],
    use_container_width=True,
    hide_index=True,
)

st.info("Use environment variables or a .env file to configure secrets, service URLs, and deployment settings.")
