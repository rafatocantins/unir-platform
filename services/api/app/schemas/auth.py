"""Schemas de autenticação."""

import json

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    location: Optional[str] = None
    interests: Optional[list[str]] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    location: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[list[str]] = None
    is_verified: bool
    is_politician: bool
    politician_role: Optional[str] = None
    has_signed: bool
    quota_amount: str
    created_at: datetime

    @field_validator("interests", mode="before")
    @classmethod
    def parse_interests(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[list[str]] = None
    avatar_url: Optional[str] = None


class SignatureData(BaseModel):
    cc_number: str
    birth_date: str
    postal_code: str
    address: str
    quota_amount: Optional[str] = "0"
    interests: Optional[list[str]] = None
