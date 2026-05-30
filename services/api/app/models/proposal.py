"""Modelo de Proposta (proposta política submetida por membros)."""

from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)  # resumo de 300 chars
    content = Column(Text, nullable=True)  # conteúdo completo
    category = Column(String(50), nullable=False, index=True)
    status = Column(
        String(20),
        default="submitted",
        index=True,
        # submitted → voting → approved → in_progress → completed / rejected
    )
    is_anonymous = Column(Boolean, default=False)
    location = Column(String(255), nullable=True)  # proposta local
    tags = Column(Text, nullable=True)  # JSON array
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    author = relationship("User", backref="proposals")
    votes = relationship("Vote", backref="proposal", lazy="dynamic")
    timeline = relationship("TimelineEvent", backref="proposal", lazy="dynamic",
                             order_by="TimelineEvent.created_at")
