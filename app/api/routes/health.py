from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.health import HealthLog
from app.schemas.health import HealthLogCreate, HealthLogUpdate, HealthLogOut, HealthSummary
from app.services import health as health_service

router = APIRouter(prefix="/health", tags=["Saúde Física"])


@router.get("/today", response_model=HealthLogOut | None)
def today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna o registro de hoje, ou null se ainda não foi criado."""
    return health_service.get_log_by_date(db, current_user.id, date.today())


@router.post("/log", response_model=HealthLogOut)
def upsert_log(
    data: HealthLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria ou atualiza o registro de um dia (idempotente por data)."""
    return health_service.upsert_log(db, current_user.id, data)


@router.patch("/log/{log_date}", response_model=HealthLogOut)
def patch_log(
    log_date: date,
    data: HealthLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza campos específicos do registro de um dia."""
    log = health_service.get_log_by_date(db, current_user.id, log_date)
    if not log:
        raise HTTPException(status_code=404, detail="Registro não encontrado para essa data.")
    return health_service.update_log(db, log, data)


@router.get("/history", response_model=list[HealthLogOut])
def history(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Histórico dos últimos N dias (padrão: 30)."""
    return health_service.get_history(db, current_user.id, days)


@router.get("/summary", response_model=HealthSummary)
def summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resumo dos últimos 7 dias."""
    return health_service.get_weekly_summary(db, current_user.id)
