"""Modelo de Evento (presencial, online, híbrido)."""

from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)
    online_url = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    max_participants = Column(Integer, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    rsvps = relationship("EventRSVP", backref="event", lazy="dynamic")


class EventRSVP(Base):
    __tablename__ = "event_rsvps"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    event_id = Column(String(36), ForeignKey("events.id"), primary_key=True)
    status = Column(String(20), default="confirmed")  # 'confirmed', 'maybe', 'declined'
    created_at = Column(DateTime, default=datetime.utcnow)
