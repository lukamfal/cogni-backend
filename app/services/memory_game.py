import random
from app.models.game_session import Difficulty

# Banco de ícones por categoria
ICON_POOL = [
    "🌸", "🦋", "🌻", "⭐", "🐘", "🍎", "🚗", "🏠",
    "🌈", "🐶", "🎵", "❤️", "🍦", "⚽", "🌙", "🦁",
    "🍓", "🎈", "🐠", "🌿", "🍕", "🎸", "🏆", "🦜",
]

DIFFICULTY_CONFIG = {
    Difficulty.EASY:   {"pairs": 4,  "time_limit": 120, "show_preview_seconds": 3},
    Difficulty.MEDIUM: {"pairs": 6,  "time_limit": 90,  "show_preview_seconds": 2},
    Difficulty.HARD:   {"pairs": 8,  "time_limit": 60,  "show_preview_seconds": 0},
}


def generate_board(difficulty: Difficulty) -> dict:
    """Gera o tabuleiro embaralhado para o jogo da memória."""
    cfg = DIFFICULTY_CONFIG[difficulty]
    selected = random.sample(ICON_POOL, cfg["pairs"])
    board = selected * 2
    random.shuffle(board)

    return {
        "pairs": cfg["pairs"],
        "time_limit_seconds": cfg["time_limit"],
        "show_preview_seconds": cfg["show_preview_seconds"],
        "items": board,
    }


def calculate_score(
    pairs: int,
    correct_pairs: int,
    duration_seconds: int,
    time_limit: int,
    difficulty: Difficulty,
) -> int:
    """Calcula pontuação baseada em acertos, tempo e dificuldade."""
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    base = correct_pairs * 50
    time_bonus = max(0, (time_limit - duration_seconds) * 2)
    perfect_bonus = 100 if correct_pairs == pairs else 0
    return int((base + time_bonus + perfect_bonus) * multipliers[difficulty])
