"""Modelo de Timeline — registo de eventos de impacto nas propostas."""

from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey

from app.core.database import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    evidence_urls = Column(Text, nullable=True)  # JSON array de URLs
    created_at = Column(DateTime, default=datetime.utcnow)
