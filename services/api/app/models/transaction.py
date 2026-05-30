"""Modelo de Transação Financeira — transparência total."""

from datetime import datetime, date

from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, Index

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    type = Column(String(20), nullable=False)  # 'income', 'expense'
    category = Column(String(50), nullable=True)  # 'campanha', 'operação', 'evento'
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    description = Column(Text, nullable=False)
    receipt_url = Column(Text, nullable=True)
    date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_transactions_type", "type"),
        Index("idx_transactions_date", "date"),
    )
