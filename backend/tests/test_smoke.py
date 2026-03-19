import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.json()
    assert json_data['status'] == 'ok'
    assert 'service' in json_data
    assert 'database' in json_data
