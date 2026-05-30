"""Rotas de autenticação: registo, login, perfil."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user, HTTPAuthorizationCredentials, Depends
from app.core.helpers import json_dumps, json_loads
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
    SignatureData,
)

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Regista um novo utilizador."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já registado",
        )

    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        location=data.location,
        interests=json_dumps(data.interests),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Autentica um utilizador existente."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou password incorretos",
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou password incorretos",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Devolve o perfil do utilizador autenticado."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o perfil do utilizador autenticado."""
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/sign", response_model=UserResponse)
def sign_as_member(
    data: SignatureData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Regista a assinatura formal do utilizador como membro UNIR."""
    current_user.cc_number = data.cc_number
    current_user.birth_date = data.birth_date
    current_user.postal_code = data.postal_code
    current_user.address = data.address
    current_user.quota_amount = data.quota_amount
    current_user.has_signed = True
    current_user.signed_at = datetime.utcnow()

    if data.interests:
        current_user.interests = json_dumps(data.interests)

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
