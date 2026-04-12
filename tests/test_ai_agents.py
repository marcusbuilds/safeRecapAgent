import pytest
import requests

def test_agent_run_endpoint():
    pytest.importorskip("requests")
    url = "http://localhost:8000/agent/run"
    payload = {
        "user_input": "Summarize this meeting: roadmap review and owner follow-up.",
        "history": []
    }
    response = requests.post(url, json=payload, timeout=5)
    if response.status_code == 401:
        pytest.skip("Local server requires X-API-Key")
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
