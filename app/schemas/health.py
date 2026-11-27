from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.health import Mood


class HealthLogCreate(BaseModel):
    log_date: date
    water_cups: int = Field(0, ge=0, le=30)
    water_goal: int = Field(8, ge=1, le=30)
    steps: int = Field(0, ge=0)
    steps_goal: int = Field(3000, ge=0)
    exercise_minutes: int = Field(0, ge=0, le=1440)
    sleep_hours: float = Field(0.0, ge=0.0, le=24.0)
    mood: Optional[Mood] = None
    medication_taken: bool = False
    medication_notes: Optional[str] = Field(None, max_length=300)
    notes: Optional[str] = Field(None, max_length=500)


class HealthLogUpdate(BaseModel):
    water_cups: Optional[int] = Field(None, ge=0, le=30)
    water_goal: Optional[int] = Field(None, ge=1, le=30)
    steps: Optional[int] = Field(None, ge=0)
    steps_goal: Optional[int] = Field(None, ge=0)
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440)
    sleep_hours: Optional[float] = Field(None, ge=0.0, le=24.0)
    mood: Optional[Mood] = None
    medication_taken: Optional[bool] = None
    medication_notes: Optional[str] = Field(None, max_length=300)
    notes: Optional[str] = Field(None, max_length=500)


class HealthLogOut(BaseModel):
    id: int
    user_id: int
    log_date: date
    water_cups: int
    water_goal: int
    steps: int
    steps_goal: int
    exercise_minutes: int
    sleep_hours: float
    mood: Optional[Mood]
    medication_taken: bool
    medication_notes: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class HealthSummary(BaseModel):
    """Resumo dos últimos 7 dias."""
    avg_water_cups: float
    avg_sleep_hours: float
    avg_steps: float
    avg_exercise_minutes: float
    medication_adherence: float  # 0.0 a 1.0
    most_common_mood: Optional[Mood]
    logs_this_week: int
