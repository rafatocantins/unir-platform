"""Rotas de Eventos e RSVP."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.event import Event, EventRSVP
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    RSVPRequest,
    RSVPResponse,
)

router = APIRouter(prefix="/events", tags=["eventos"])


@router.get("", response_model=list[EventResponse])
def list_events(
    upcoming: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Lista eventos (por defeito, apenas futuros)."""
    query = db.query(Event)
    if upcoming:
        query = query.filter(Event.start_date >= datetime.utcnow())
    query = query.order_by(Event.start_date).all()

    results = []
    for event in query:
        response = EventResponse.model_validate(event)
        response.rsvp_count = event.rsvps.count()
        results.append(response)
    return results


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Obtém detalhe de um evento."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    response = EventResponse.model_validate(event)
    response.rsvp_count = event.rsvps.count()
    return response


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um novo evento."""
    event = Event(
        title=data.title,
        description=data.description,
        event_type=data.event_type,
        location=data.location,
        online_url=data.online_url,
        start_date=data.start_date,
        end_date=data.end_date,
        max_participants=data.max_participants,
        created_by=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    response = EventResponse.model_validate(event)
    response.rsvp_count = 0
    return response


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza um evento (só o criador)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if str(event.created_by) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não és o criador deste evento")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)

    response = EventResponse.model_validate(event)
    response.rsvp_count = event.rsvps.count()
    return response


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apaga um evento (só o criador)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if str(event.created_by) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não és o criador deste evento")

    db.delete(event)
    db.commit()


@router.post("/{event_id}/rsvp", response_model=RSVPResponse)
def rsvp_event(
    event_id: str,
    data: RSVPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirma presença num evento."""
    if data.status not in ("confirmed", "maybe", "declined"):
        raise HTTPException(status_code=400, detail="Status inválido")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # Upsert RSVP
    rsvp = db.query(EventRSVP).filter(
        EventRSVP.user_id == current_user.id,
        EventRSVP.event_id == event_id,
    ).first()

    if rsvp:
        rsvp.status = data.status
    else:
        rsvp = EventRSVP(
            user_id=current_user.id,
            event_id=event_id,
            status=data.status,
        )
        db.add(rsvp)

    db.commit()
    db.refresh(rsvp)
    return RSVPResponse.model_validate(rsvp)


@router.get("/{event_id}/rsvps", response_model=list[RSVPResponse])
def get_event_rsvps(event_id: str, db: Session = Depends(get_db)):
    """Lista RSVPs de um evento."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    rsvps = event.rsvps.all()
    return [RSVPResponse.model_validate(r) for r in rsvps]
