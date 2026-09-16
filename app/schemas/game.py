from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.game_session import GameType, Difficulty


class GameSessionCreate(BaseModel):
    game_type: GameType
    difficulty: Difficulty


class GameSessionFinish(BaseModel):
    score: int
    correct_answers: int
    total_questions: int
    duration_seconds: int
    metadata: Optional[Dict[str, Any]] = {}


class GameSessionOut(BaseModel):
    id: int
    game_type: GameType
    difficulty: Difficulty
    score: int
    accuracy: float
    duration_seconds: int
    correct_answers: int
    total_questions: int
    started_at: datetime
    finished_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---- Payloads específicos dos jogos ----

class MemoryGameConfig(BaseModel):
    """Configuração retornada ao iniciar o jogo da memória."""
    session_id: int
    pairs: int
    time_limit_seconds: int
    items: list[str]  # lista de emojis/ícones embaralhados (tamanho = pairs * 2)


class MathQuestion(BaseModel):
    session_id: int
    question_number: int
    total_questions: int
    expression: str   # ex: "12 + 7"
    options: list[int]  # 4 alternativas
    time_limit_seconds: int


class MathAnswer(BaseModel):
    session_id: int
    question_number: int
    answer: int


class FaceQuestion(BaseModel):
    session_id: int
    question_number: int
    total_questions: int
    photo_url: str
    options: list[str]  # nomes para escolher
    time_limit_seconds: int


class WordQuestion(BaseModel):
    session_id: int
    question_number: int
    total_questions: int
    masked_word: str   # ex: "C_SA" (para CASA)
    hint: str          # ex: "Lugar onde moramos"
    options: list[str] # letras ou palavras completas
    time_limit_seconds: int
