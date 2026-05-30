"""Rotas públicas — submissão de assinaturas sem autenticação."""

from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.core.helpers import json_dumps
from app.models.user import User

router = APIRouter(prefix="/public", tags=["público"])


class PublicSignRequest(BaseModel):
    email: str
    name: str
    postal: str
    morada: str
    cc: str
    nascimento: str
    interesses: Optional[str] = ""
    quota: Optional[str] = "0"


class PublicSignResponse(BaseModel):
    success: bool
    message: str


class CountResponse(BaseModel):
    total: int
    remaining: int
    progress_pct: float


ASSINATURAS_NECESSARIAS = 7500


@router.post("/sign", response_model=PublicSignResponse)
def public_sign(data: PublicSignRequest, db: Session = Depends(get_db)):
    """Regista uma assinatura pública (sem login)."""

    # Validar campos obrigatórios
    if not data.email or not data.name or not data.cc or not data.nascimento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campos obrigatórios: email, nome, cc, nascimento"
        )

    # Verificar se email ou CC já foram registados
    existing = db.query(User).filter(
        (User.email == data.email) | (User.cc_number == data.cc)
    ).first()
    if existing:
        return PublicSignResponse(
            success=True,
            message="Já recebemos a tua assinatura! Obrigado pelo teu apoio."
        )

    # Criar utilizador com password aleatória (nunca vai fazer login)
    random_password = secrets.token_hex(16)
    interests_list = [i.strip() for i in data.interesses.split(",") if i.strip()] if data.interesses else None

    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(random_password),
        location="",
        interests=json_dumps(interests_list),
        cc_number=data.cc,
        birth_date=data.nascimento,
        postal_code=data.postal,
        address=data.morada,
        quota_amount=data.quota,
        has_signed=True,
        signed_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()

    return PublicSignResponse(
        success=True,
        message="Assinatura registada com sucesso! Contamos contigo para construir um Portugal diferente."
    )


@router.get("/count", response_model=CountResponse)
def get_count(db: Session = Depends(get_db)):
    """Devolve o total de assinaturas, restantes e percentagem."""
    total = db.query(User).filter(User.has_signed == True).count()
    remaining = max(0, ASSINATURAS_NECESSARIAS - total)
    progress = min(100.0, round((total / ASSINATURAS_NECESSARIAS) * 100, 1))
    return CountResponse(
        total=total,
        remaining=remaining,
        progress_pct=progress,
    )
