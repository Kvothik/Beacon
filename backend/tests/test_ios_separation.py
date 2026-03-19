import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_ios_lane_placeholder():
    # Minimal test to mark iOS lane separate and optional
    response = client.get('/health')
    assert response.status_code == 200
