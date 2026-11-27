from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GameType(str, enum.Enum):
    MEMORY = "memory"
    MATH = "math"
    FACE = "face"
    WORD = "word"
    RACE = "race"
    TUG = "tug"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_type = Column(SAEnum(GameType), nullable=False)
    difficulty = Column(SAEnum(Difficulty), nullable=False)

    # métricas da sessão
    score = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)       # 0.0 a 1.0
    duration_seconds = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)

    # dados extras do jogo (ex: sequência de erros, tempo por pergunta)
    game_metadata = Column(JSON, default={})

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="game_sessions")
