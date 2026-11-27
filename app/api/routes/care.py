"""Acompanhamento: familiares e cuidadores veem o progresso de quem joga, com permissão."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes import scores as scores_routes
from app.core.database import get_db
from app.models.care_link import CareLink, CareLinkStatus
from app.models.user import User, UserRole
from app.schemas.care import (
    CareRequestCreate, FollowingOut, IncomingRequestOut, FollowerOut, ElderOverview, ScoreSummary,
)
from app.services import health as health_service

router = APIRouter(prefix="/care", tags=["Acompanhamento"])

MAX_LINKS_PER_CAREGIVER = 20


def _require_caregiver(user: User) -> None:
    if user.role != UserRole.CAREGIVER:
        raise HTTPException(403, "Só contas de quem acompanha podem fazer isso.")


# ---------- quem acompanha ----------
@router.post("/requests", status_code=202)
def create_request(
    payload: CareRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pede para acompanhar alguém pelo e-mail.

    A resposta é sempre a mesma, exista ou não a conta, para ninguém usar isto
    para descobrir quais e-mails estão cadastrados.
    """
    _require_caregiver(current_user)
    email = payload.elder_email.lower()
    if email == current_user.email.lower():
        raise HTTPException(400, "Use o e-mail da pessoa que você quer acompanhar.")

    exists = db.query(CareLink).filter(
        CareLink.caregiver_id == current_user.id, CareLink.elder_email == email,
    ).first()
    if not exists:
        count = db.query(CareLink).filter(CareLink.caregiver_id == current_user.id).count()
        if count >= MAX_LINKS_PER_CAREGIVER:
            raise HTTPException(429, "Você chegou ao limite de pedidos. Cancele algum antes de pedir outro.")
        db.add(CareLink(caregiver_id=current_user.id, elder_email=email, status=CareLinkStatus.PENDING))
        db.commit()
    return {"detail": "Pedido enviado. Ele aparece para a pessoa quando ela entrar no CogniMente."}


@router.get("/following", response_model=list[FollowingOut])
def following(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_caregiver(current_user)
    links = db.query(CareLink).filter(CareLink.caregiver_id == current_user.id).order_by(CareLink.created_at.desc()).all()
    out = []
    for link in links:
        accepted = link.status == CareLinkStatus.ACCEPTED and link.elder is not None
        out.append(FollowingOut(
            id=link.id,
            status=link.status,
            elder_email=link.elder_email,
            elder_id=link.elder_id if accepted else None,
            elder_name=link.elder.name if accepted else None,
            created_at=link.created_at,
            accepted_at=link.accepted_at,
        ))
    return out


@router.get("/elders/{elder_id}/overview", response_model=ElderOverview)
def elder_overview(elder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_caregiver(current_user)
    link = db.query(CareLink).filter(
        CareLink.caregiver_id == current_user.id,
        CareLink.elder_id == elder_id,
        CareLink.status == CareLinkStatus.ACCEPTED,
    ).first()
    # Sem permissão, responde como se a pessoa não existisse.
    if not link or not link.elder:
        raise HTTPException(404, "Pessoa não encontrada")
    elder = link.elder
    return ElderOverview(
        elder_id=elder.id,
        elder_name=elder.name,
        summary=ScoreSummary(**scores_routes.summary(current_user=elder, db=db)),
        recent_sessions=scores_routes.history(game_type=None, limit=50, current_user=elder, db=db),
        health_summary=health_service.get_weekly_summary(db, elder.id),
        health_week=health_service.get_history(db, elder.id, 7),
    )


# ---------- quem joga ----------
def _incoming_query(user: User, db: Session):
    return db.query(CareLink).filter(
        CareLink.elder_email == user.email.lower(),
        CareLink.status == CareLinkStatus.PENDING,
        CareLink.caregiver_id != user.id,
    )


@router.get("/requests", response_model=list[IncomingRequestOut])
def incoming_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [
        IncomingRequestOut(id=l.id, caregiver_name=l.caregiver.name, caregiver_email=l.caregiver.email, created_at=l.created_at)
        for l in _incoming_query(current_user, db).all()
    ]


@router.post("/requests/{link_id}/accept", response_model=FollowerOut)
def accept_request(link_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    link = _incoming_query(current_user, db).filter(CareLink.id == link_id).first()
    if not link:
        raise HTTPException(404, "Pedido não encontrado")
    link.status = CareLinkStatus.ACCEPTED
    link.elder_id = current_user.id
    link.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(link)
    return FollowerOut(id=link.id, caregiver_name=link.caregiver.name, caregiver_email=link.caregiver.email, accepted_at=link.accepted_at)


@router.post("/requests/{link_id}/decline", status_code=204)
def decline_request(link_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    link = _incoming_query(current_user, db).filter(CareLink.id == link_id).first()
    if not link:
        raise HTTPException(404, "Pedido não encontrado")
    db.delete(link)
    db.commit()


@router.get("/followers", response_model=list[FollowerOut])
def followers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    links = db.query(CareLink).filter(
        CareLink.elder_id == current_user.id, CareLink.status == CareLinkStatus.ACCEPTED,
    ).all()
    return [
        FollowerOut(id=l.id, caregiver_name=l.caregiver.name, caregiver_email=l.caregiver.email, accepted_at=l.accepted_at)
        for l in links
    ]


# ---------- os dois lados ----------
@router.delete("/links/{link_id}", status_code=204)
def remove_link(link_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Quem acompanha cancela o pedido ou para de acompanhar; quem joga tira a permissão."""
    link = db.query(CareLink).filter(CareLink.id == link_id).first()
    if not link or current_user.id not in (link.caregiver_id, link.elder_id):
        raise HTTPException(404, "Não encontrado")
    db.delete(link)
    db.commit()
