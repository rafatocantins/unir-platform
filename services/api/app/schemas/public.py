"""Schemas para endpoints públicos (landing page)."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class PublicSignRequest(BaseModel):
    """Registo + assinatura num único passo (vindo da landing page)."""
    email: str
    name: str
    postal: str
    morada: str
    cc: str
    nascimento: str
    interesses: Optional[str] = ""
    quota: str = "0"


class PublicSignResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
