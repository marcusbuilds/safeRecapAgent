from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class MeetingOut(BaseModel):
    id: UUID
    title: Optional[str]
    sanitized_transcript: Optional[str]
    source_type: Optional[str]
    risk_level: Optional[str]
    meta: dict

    class Config:
        orm_mode = True
