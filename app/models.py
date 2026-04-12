from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
from .database import Base
from datetime import datetime
import uuid

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True))
    sanitized_transcript = Column(Text, nullable=True)
    source_type = Column(String(20), nullable=False, server_default="text")
    risk_level = Column(String(10), nullable=False, server_default="low")
    meta = Column(JSON, nullable=False, server_default="{}")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=True)
    decisions = Column(JSON, nullable=False, server_default="[]")
    open_questions = Column(JSON, nullable=False, server_default="[]")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    task = Column(Text, nullable=False)
    urgency = Column(String(10), nullable=False, server_default="medium")
    owner_role = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(200), nullable=False)
    action = Column(String(200), nullable=False)
    reason = Column(Text, nullable=True)
    meta = Column(JSON, nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
