from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.models.care_link import CareLinkStatus
from app.schemas.game import GameSessionOut
from app.schemas.health import HealthLogOut, HealthSummary


class CareRequestCreate(BaseModel):
    elder_email: EmailStr


class FollowingOut(BaseModel):
    """Para quem acompanha: um pedido ou uma pessoa acompanhada."""
    id: int
    status: CareLinkStatus
    elder_email: str
    elder_id: Optional[int]     # só depois de permitido
    elder_name: Optional[str]   # só depois de permitido
    created_at: Optional[datetime]
    accepted_at: Optional[datetime]


class IncomingRequestOut(BaseModel):
    """Para quem joga: alguém pedindo para acompanhar."""
    id: int
    caregiver_name: str
    caregiver_email: str
    created_at: Optional[datetime]


class FollowerOut(BaseModel):
    """Para quem joga: quem já acompanha."""
    id: int
    caregiver_name: str
    caregiver_email: str
    accepted_at: Optional[datetime]


class ScoreSummary(BaseModel):
    total_sessions: int
    total_points: int
    streak_days: int


class ElderOverview(BaseModel):
    """O que quem acompanha consegue ver de quem joga."""
    elder_id: int
    elder_name: str
    summary: ScoreSummary
    recent_sessions: list[GameSessionOut]
    health_summary: HealthSummary
    health_week: list[HealthLogOut]
