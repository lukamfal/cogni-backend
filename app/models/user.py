from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ELDER = "elder"          # idoso que joga
    CAREGIVER = "caregiver"  # cuidador/familiar que acompanha


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.ELDER, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # elder pode ter um cuidador vinculado
    caregiver_id = Column(Integer, nullable=True)

    # relacionamentos
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")
    health_logs = relationship("HealthLog", back_populates="user", cascade="all, delete-orphan")
