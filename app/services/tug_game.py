"""Cabo de guerra: tocar no botão um número de vezes antes do tempo acabar."""
from app.models.game_session import Difficulty

DIFFICULTY_CONFIG = {
    Difficulty.EASY:   {"target_clicks": 30, "time_limit_seconds": 60},
    Difficulty.MEDIUM: {"target_clicks": 30, "time_limit_seconds": 40},
    Difficulty.HARD:   {"target_clicks": 30, "time_limit_seconds": 25},
}

# Ninguém faz 30 toques em menos que isso com o dedo; abaixo é automação.
MIN_SECONDS_TO_WIN = 3
# Contagem regressiva do app antes de valer (3, 2, 1).
COUNTDOWN_SECONDS = 3


def config(difficulty: Difficulty) -> dict:
    return dict(DIFFICULTY_CONFIG[difficulty])


def calculate_score(won: bool, clicks: int, seconds_left: int, difficulty: Difficulty) -> int:
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    if won:
        return int((100 + max(0, seconds_left) * 3) * multipliers[difficulty])
    # Quem não venceu ganha um pouco pelo esforço.
    return int(clicks * 2 * multipliers[difficulty])
