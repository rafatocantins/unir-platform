"""Modelo de Voto em propostas."""

from datetime import datetime

from sqlalchemy import Column, SmallInteger, Text, DateTime, ForeignKey, UniqueConstraint, String

from app.core.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    vote_value = Column(SmallInteger, nullable=False)  # 1 (sim), -1 (não), 0 (abstenção)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "proposal_id", name="uq_user_proposal_vote"),
    )
