from .database import SessionLocal
from . import models
from uuid import UUID
from sqlalchemy.exc import NoResultFound

def create_meeting(payload):
    db = SessionLocal()
    try:
        m = models.Meeting(
            title=payload.title,
            sanitized_transcript=payload.sanitized_transcript,
            source_type=payload.source_type,
            meta=payload.meta or {}
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return m
    finally:
        db.close()

def get_meeting(meeting_id: UUID):
    db = SessionLocal()
    try:
        return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).one_or_none()
    finally:
        db.close()
