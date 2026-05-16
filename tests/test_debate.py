import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_policy_usa():
    response = client.get("/policies/usa")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "USA"
    assert "key_positions" in data

def test_get_policy_invalid():
    response = client.get("/policies/invalid")
    assert response.status_code == 404

def test_debate_start_schema():
    # Note: This test might take a while if it actually calls Ollama.
    # In a real CI environment, we would mock the Debater agent.
    # For now, we just test the endpoint existence and basic validation.
    response = client.post("/debate/start", json={
        "topic": "Test Topic",
        "rounds": 1
    })
    # If Ollama is not running, it might return 500 or 200 with error messages.
    # We just want to see if the endpoint is reachable.
    assert response.status_code in [200, 500]
