"""Modelo de Utilizador / Militante UNIR."""

from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # NULL para magic link
    avatar_url = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)  # cidade/distrito
    bio = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)  # JSON array ['educação', 'ambiente', ...]
    is_verified = Column(Boolean, default=False)
    is_politician = Column(Boolean, default=False)
    politician_role = Column(String(100), nullable=True)

    # Dados de assinatura (RGPD)
    cc_number = Column(String(20), nullable=True)
    birth_date = Column(String(10), nullable=True)
    postal_code = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    has_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime, nullable=True)

    # Quota
    quota_amount = Column(String(10), default="0")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
