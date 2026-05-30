"""Schemas de Propostas e Votações."""

import json

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def _parse_uuid(v):
    return str(v) if not isinstance(v, str) else v


class ProposalCreate(BaseModel):
    title: str
    summary: str
    content: Optional[str] = None
    category: str
    is_anonymous: bool = False
    location: Optional[str] = None
    tags: Optional[list[str]] = None


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[list[str]] = None


class ProposalResponse(BaseModel):
    id: str
    user_id: str

    @field_validator("id", "user_id", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v)
    title: str
    summary: str
    content: Optional[str] = None
    category: str
    status: str
    is_anonymous: bool
    location: Optional[str] = None
    tags: Optional[list[str]] = None
    upvotes: int
    downvotes: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True


class ProposalListResponse(BaseModel):
    items: list[ProposalResponse]
    total: int
    page: int
    page_size: int


class VoteRequest(BaseModel):
    vote_value: int  # 1, -1, or 0
    comment: Optional[str] = None


class VoteResponse(BaseModel):
    id: str
    proposal_id: str

    @field_validator("id", "proposal_id", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v)
    vote_value: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TimelineEventCreate(BaseModel):
    event_type: str
    description: str
    evidence_urls: Optional[list[str]] = None


class TimelineEventResponse(BaseModel):
    id: str
    proposal_id: str
    event_type: str
    description: str
    actor_id: Optional[str] = None

    @field_validator("id", "proposal_id", "actor_id", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v) if v is not None else v
    evidence_urls: Optional[list[str]] = None
    created_at: datetime

    @field_validator("evidence_urls", mode="before")
    @classmethod
    def parse_evidence(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True
