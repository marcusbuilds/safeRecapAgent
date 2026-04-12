"""
# app/main.py

"""

import os
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from uuid import uuid4
import uvicorn
from .ai_client import get_llm_client
from .filters import LocalFilterEngine
from . import crud, schemas, database
from .ai_agents.router import router as agent_router

app = FastAPI(title="safeRecap", docs_url="/saferecap")

database.init_db()


# In-memory stores for the prototype (replace with DB in prod)
MEETINGS = {}
SENSITIVE = {}


llm_client = get_llm_client()
filter_engine = LocalFilterEngine()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)):
    configured_api_key = os.environ.get("APP_API_KEY", "").strip()
    if not configured_api_key:
        return
    if api_key != configured_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app.include_router(agent_router, dependencies=[Depends(require_api_key)])


class RawMeeting(BaseModel):
    meeting_id: str | None = None
    text: str


class SensitivePayload(BaseModel):
    meeting_id: str
    forbidden_terms: list[str] = []
    rules: list[dict] = []


@app.post('/meetings/raw', dependencies=[Depends(require_api_key)])
async def upload_meeting(payload: RawMeeting):
    mid = payload.meeting_id or str(uuid4())
    MEETINGS[mid] = payload.text
    return {"meeting_id": mid, "status": "stored"}


@app.post('/meetings/sensitive', dependencies=[Depends(require_api_key)])
async def upload_sensitive(payload: SensitivePayload):
    # NOTE: in prod encrypt and store in DB
    SENSITIVE[payload.meeting_id] = {
        "forbidden_terms": payload.forbidden_terms,
        "rules": payload.rules,
    }
    filter_engine.add_context(payload.meeting_id, SENSITIVE[payload.meeting_id])
    return {"status": "ok"}


@app.get('/meetings/{meeting_id}/summary', dependencies=[Depends(require_api_key)])
async def get_summary(meeting_id: str):
    try:
        raw = MEETINGS.get(meeting_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Meeting not found")

        sanitized = filter_engine.sanitize_for_llm(meeting_id, raw)

        # 2) call LLM for summary and action items using the full meta prompt from concept
        prompt = (
            "You are an enterprise-grade Meeting Intelligence Agent.\n"
            "You will ONLY receive sanitized, non-sensitive meeting content.\n"
            "You must behave as if the organization operates in a regulated, compliance-sensitive industry (e.g. LegalTech / FinTech / Healthcare).\n"
            "\nYour responsibilities:\n"
            "1. Generate a concise, accurate meeting summary\n"
            "2. Identify key decisions\n"
            "3. Produce clear, actionable action items\n"
            "4. Highlight unresolved questions or risks\n"
            "5. Do NOT invent facts\n"
            "6. Do NOT include personal, financial, or sensitive information\n"
            "7. Assume all PII has been removed\n"
            "\nFormat your response as valid JSON exactly in this structure:\n"
            '{\n'
            '  "summary": "<3-6 sentence executive summary>",\n'
            '  "decisions": [\n'
            '    "<bullet point>",\n'
            '    "<bullet point>"\n'
            '  ],\n'
            '  "action_items": [\n'
            '    {\n'
            '      "task": "string",\n'
            '      "urgency": "low | medium | high",\n'
            '      "owner": "role-based (not a person name)",\n'
            '      "notes": "string"\n'
            '    }\n'
            '  ],\n'
            '  "open_questions": [\n'
            '    "<question>",\n'
            '    "<question>"\n'
            '  ],\n'
            '  "risk_level": "low | medium | high"\n'
            '}\n'
            "\nStyle Guide:\n"
            "- Be concise and factual\n"
            "- Use neutral, professional language\n"
            "- Do not hallucinate missing content\n"
            "- If information is unavailable, respond with: 'Insufficient data in transcript'\n"
            "- Prefer clarity over creativity\n"
            "\nNow process this meeting transcript:\n"
            f"{sanitized}"
        )
        llm_out = await llm_client.generate(prompt=prompt)

        # 3) parse llm_out (assume JSON) — robust parsing in prod
        # For the prototype, expect llm_out to be a dict
        # 4) perform local enforcement (remove forbidden terms, apply rules)
        final = filter_engine.enforce_rules(meeting_id, llm_out)

        # 5) return partially redacted explanation & final output
        return {"meeting_id": meeting_id, "result": final}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Summary generation failed")


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
