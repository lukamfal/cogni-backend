from sqlalchemy import Column, Integer, Float, String, Boolean, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base
import enum


class Mood(str, enum.Enum):
    GREAT = "great"      # 😄
    GOOD = "good"        # 🙂
    NEUTRAL = "neutral"  # 😐
    BAD = "bad"          # 😕
    AWFUL = "awful"      # 😢


class HealthLog(Base):
    """Registro diário de saúde física do idoso."""
    __tablename__ = "health_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Data do registro (um por dia)
    log_date = Column(Date, nullable=False)

    # Hidratação (copos de água, 250ml cada)
    water_cups = Column(Integer, default=0)
    water_goal = Column(Integer, default=8)

    # Atividade física
    steps = Column(Integer, default=0)
    steps_goal = Column(Integer, default=3000)
    exercise_minutes = Column(Integer, default=0)

    # Sono (horas)
    sleep_hours = Column(Float, default=0.0)

    # Humor
    mood = Column(SAEnum(Mood), nullable=True)

    # Medicação tomada no dia
    medication_taken = Column(Boolean, default=False)
    medication_notes = Column(String(300), nullable=True)

    # Observações livres
    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="health_logs")
