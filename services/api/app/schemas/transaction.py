"""Schemas de Transparência Financeira."""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


def _parse_uuid(v):
    return str(v) if not isinstance(v, str) else v


class TransactionCreate(BaseModel):
    type: str  # 'income', 'expense'
    category: Optional[str] = None
    amount: float
    currency: str = "EUR"
    description: str
    receipt_url: Optional[str] = None
    date: Optional[date] = None


class TransactionResponse(BaseModel):
    id: str
    type: str
    category: Optional[str] = None
    amount: float
    currency: str
    description: str
    receipt_url: Optional[str] = None
    date: date
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def parse_uuid(cls, v):
        return _parse_uuid(v)

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
