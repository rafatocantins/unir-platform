"""Schemas de Eventos."""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def _parse_uuid(v):
    return str(v) if not isinstance(v, str) else v


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str  # 'presencial', 'online', 'hibrido'
    location: Optional[str] = None
    online_url: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    online_url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = None


class EventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    event_type: str
    location: Optional[str] = None
    online_url: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = None
    created_by: str
    rsvp_count: int = 0
    created_at: datetime

    @field_validator("id", "created_by", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v)

    class Config:
        from_attributes = True


class RSVPRequest(BaseModel):
    status: str = "confirmed"  # 'confirmed', 'maybe', 'declined'


class RSVPResponse(BaseModel):
    user_id: str
    event_id: str
    status: str
    created_at: datetime

    @field_validator("user_id", "event_id", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v)

    class Config:
        from_attributes = True
