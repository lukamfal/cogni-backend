from pydantic import BaseModel
from datetime import datetime
from app.models.game_session import GameType, Difficulty


class ScoreOut(BaseModel):
    id: int
    game_type: GameType
    difficulty: Difficulty
    value: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    user_name: str
    score: int
    game_type: GameType
    difficulty: Difficulty
