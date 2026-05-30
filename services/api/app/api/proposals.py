"""Rotas de Propostas e Votações."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.helpers import json_dumps
from app.models.user import User
from app.models.proposal import Proposal
from app.models.vote import Vote
from app.models.timeline import TimelineEvent
from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalListResponse,
    VoteRequest,
    VoteResponse,
    TimelineEventCreate,
    TimelineEventResponse,
)

router = APIRouter(prefix="/proposals", tags=["propostas"])


@router.get("", response_model=ProposalListResponse)
def list_proposals(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista propostas com filtros e paginação."""
    query = db.query(Proposal)

    if status_filter:
        query = query.filter(Proposal.status == status_filter)
    if category:
        query = query.filter(Proposal.category == category)

    total = query.count()
    query = query.order_by(desc(Proposal.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    items = []
    for p in query.all():
        item = ProposalResponse.model_validate(p)
        if not p.is_anonymous:
            item.author_name = p.author.name if p.author else None
        items.append(item)

    return ProposalListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Obtém detalhe de uma proposta."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    response = ProposalResponse.model_validate(proposal)
    if not proposal.is_anonymous:
        response.author_name = proposal.author.name if proposal.author else None
    return response


@router.post("", response_model=ProposalResponse, status_code=201)
def create_proposal(
    data: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria uma nova proposta."""
    proposal = Proposal(
        user_id=current_user.id,
        title=data.title,
        summary=data.summary,
        content=data.content,
        category=data.category,
        is_anonymous=data.is_anonymous,
        location=data.location,
        tags=json_dumps(data.tags),
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    response = ProposalResponse.model_validate(proposal)
    if not proposal.is_anonymous:
        response.author_name = current_user.name
    return response


@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: str,
    data: ProposalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza uma proposta (só o autor)."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    if str(proposal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não és o autor desta proposta")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(proposal, field, value)
    db.commit()
    db.refresh(proposal)

    response = ProposalResponse.model_validate(proposal)
    if not proposal.is_anonymous:
        response.author_name = current_user.name
    return response


@router.delete("/{proposal_id}", status_code=204)
def delete_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apaga uma proposta (só o autor)."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    if str(proposal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não és o autor desta proposta")

    db.delete(proposal)
    db.commit()


@router.post("/{proposal_id}/vote", response_model=VoteResponse)
def vote_on_proposal(
    proposal_id: str,
    data: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vota numa proposta (1=sim, -1=não, 0=abstenção)."""
    if data.vote_value not in (-1, 0, 1):
        raise HTTPException(status_code=400, detail="Voto inválido. Use 1, -1 ou 0")

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    if proposal.status not in ("voting", "submitted"):
        raise HTTPException(status_code=400, detail="Esta proposta não está em votação")

    # Upsert: se já votou, atualiza
    existing = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.proposal_id == proposal_id,
    ).first()

    if existing:
        existing.vote_value = data.vote_value
        existing.comment = data.comment
    else:
        existing = Vote(
            user_id=current_user.id,
            proposal_id=proposal_id,
            vote_value=data.vote_value,
            comment=data.comment,
        )
        db.add(existing)

    # Atualiza contagens na proposta
    votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).all()
    proposal.upvotes = sum(1 for v in votes if v.vote_value == 1)
    proposal.downvotes = sum(1 for v in votes if v.vote_value == -1)

    db.commit()
    db.refresh(existing)
    return VoteResponse.model_validate(existing)


@router.get("/{proposal_id}/votes", response_model=list[VoteResponse])
def get_proposal_votes(
    proposal_id: str,
    db: Session = Depends(get_db),
):
    """Obtém os votos de uma proposta."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).all()
    return [VoteResponse.model_validate(v) for v in votes]


@router.get("/{proposal_id}/timeline", response_model=list[TimelineEventResponse])
def get_proposal_timeline(
    proposal_id: str,
    db: Session = Depends(get_db),
):
    """Obtém a timeline de uma proposta."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.proposal_id == proposal_id)
        .order_by(TimelineEvent.created_at)
        .all()
    )
    return [TimelineEventResponse.model_validate(e) for e in events]


@router.post("/{proposal_id}/timeline", response_model=TimelineEventResponse, status_code=201)
def add_timeline_event(
    proposal_id: str,
    data: TimelineEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona um evento à timeline (admin/político)."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    event = TimelineEvent(
        proposal_id=proposal_id,
        event_type=data.event_type,
        description=data.description,
        actor_id=current_user.id,
        evidence_urls=json_dumps(data.evidence_urls),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return TimelineEventResponse.model_validate(event)
