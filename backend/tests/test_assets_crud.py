import pytest
from backend.tests.client import test_client as client

def test_create_and_read_asset():
    payload = {
        "hostname": "test-host-99.lab.corp",
        "ip_address": "10.99.99.10",
        "asset_type": "server",
        "criticality": "HIGH",
        "environment": "staging",
        "subnet": "10.99.99.0/24",
        "business_impact_score": 85.0
    }
    response = client.post("/api/v1/assets", json=payload)
    assert response.status_code == 201
    created = response.json()
    asset_id = created["id"]
    assert created["ip_address"] == "10.99.99.10"
    assert created["hostname"] == "test-host-99.lab.corp"

    # Reject duplicate IP
    dup_resp = client.post("/api/v1/assets", json=payload)
    assert dup_resp.status_code == 400

    # Get details
    detail_resp = client.get(f"/api/v1/assets/{asset_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == asset_id

    # Add service port
    srv_payload = {
        "asset_id": asset_id,
        "port": 8443,
        "protocol": "tcp",
        "service_name": "https-alt",
        "product": "Gunicorn",
        "version": "20.1"
    }
    srv_resp = client.post(f"/api/v1/assets/{asset_id}/services", json=srv_payload)
    assert srv_resp.status_code == 201
    assert srv_resp.json()["port"] == 8443

    # Delete asset
    del_resp = client.delete(f"/api/v1/assets/{asset_id}")
    assert del_resp.status_code == 204
