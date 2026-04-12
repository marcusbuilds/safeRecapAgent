import requests
import pytest

def test_upload_flow():
    resp = requests.post("http://localhost:8000/meetings/raw", json={
        "text": "Today we discussed the Q4 roadmap and assigned action items to the engineering team."
    }, timeout=5)
    if resp.status_code == 401:
        pytest.skip("Local server requires X-API-Key")
    assert resp.status_code == 200
    meeting_id = resp.json()["meeting_id"]

    resp = requests.post("http://localhost:8000/meetings/sensitive", json={
        "meeting_id": meeting_id,
        "forbidden_terms": ["Q4"],
        "rules": [{"id": "r1", "type": "remove_if_contains", "pattern": "engineering"}]
    }, timeout=5)
    assert resp.status_code == 200

    resp = requests.get(f"http://localhost:8000/meetings/{meeting_id}/summary", timeout=5)
    assert resp.status_code == 200
    summary = resp.json()
    assert "result" in summary
