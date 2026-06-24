from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_and_forecast_endpoint():
    client = TestClient(app)
    token_response = client.post("/token", data={"username": "analyst", "password": "analyst123"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    response = client.post("/forecast", json={"periods": 5}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 5
