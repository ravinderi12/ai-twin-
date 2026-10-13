import pytest
from backend.tests.client import test_client as client

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data
    assert data["database"] == "connected"

def test_readiness_endpoint():
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "docs_url" in response.json()
