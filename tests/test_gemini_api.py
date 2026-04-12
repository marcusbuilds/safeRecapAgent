import pytest
import requests

def test_gemini_api_detailed_prompt():
    meeting_text = (
        "Project Apollo kickoff meeting.\n"
        "Attendees: Alice, Bob, Carol, Dave.\n"
        "Agenda: 1. Timeline review 2. Budget allocation 3. Risk assessment.\n"
        "Discussion: Alice presented the initial timeline, Bob raised concerns about resource constraints.\n"
        "Carol suggested reallocating budget from marketing to development.\n"
        "Dave will prepare a risk matrix for next week.\n"
        "Action items: Alice to update the timeline, Carol to draft new budget, Dave to share risk matrix.\n"
        "\n"
        "Summarize the above meeting and list action items in JSON format with keys: summary, action_items.\n"
        "Example:\n"
        '{"summary": "The team discussed the project kickoff and assigned action items.", "action_items": ["Update timeline", "Draft new budget", "Share risk matrix"]}'
    )
    resp = requests.post(
        "http://localhost:8000/meetings/raw",
        json={"text": meeting_text},
        timeout=5,
    )
    if resp.status_code == 401:
        pytest.skip("Local server requires X-API-Key")
    assert resp.status_code == 200
    meeting_id = resp.json()["meeting_id"]

    sensitive = {
        "meeting_id": meeting_id,
        "forbidden_terms": ["budget"],
        "rules": []
    }
    resp = requests.post("http://localhost:8000/meetings/sensitive", json=sensitive, timeout=5)
    assert resp.status_code == 200

    resp = requests.get(f"http://localhost:8000/meetings/{meeting_id}/summary", timeout=5)
    try:
        result = resp.json()
        assert "summary" in result["result"]
        assert isinstance(result["result"]["summary"], str)
    except Exception as e:
        pytest.fail(f"Failed to parse or validate response: {e}")
