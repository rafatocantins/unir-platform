"""Rotas de Transparência Financeira."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionSummary,
)

router = APIRouter(prefix="/transparency", tags=["transparência"])


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    type_filter: Optional[str] = Query(None, alias="type"),
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Lista transações financeiras (público)."""
    query = db.query(Transaction)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if category:
        query = query.filter(Transaction.category == category)

    transactions = query.order_by(desc(Transaction.date)).limit(limit).all()
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/summary", response_model=TransactionSummary)
def get_summary(db: Session = Depends(get_db)):
    """Resumo financeiro (público)."""
    income = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.type == "income")
        .scalar() or 0
    )
    expense = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.type == "expense")
        .scalar() or 0
    )
    count = db.query(Transaction).count()

    return TransactionSummary(
        total_income=float(income),
        total_expense=float(expense),
        balance=float(income - expense),
        transaction_count=count,
    )


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona uma transação financeira (só admin/político)."""
    transaction = Transaction(
        type=data.type,
        category=data.category,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        receipt_url=data.receipt_url,
        date=data.date or date.today(),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return TransactionResponse.model_validate(transaction)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Detalhe de uma transação."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return TransactionResponse.model_validate(transaction)
