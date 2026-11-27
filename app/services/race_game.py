"""Corrida: reflexo. A pessoa toca quando o semáforo fica verde e corre contra carros do computador."""
from app.models.game_session import Difficulty

DIFFICULTY_CONFIG = {
    # opponents: carros do computador; cpu_*_ms: tempo de reação deles em milissegundos.
    Difficulty.EASY:   {"rounds": 3, "opponents": 1, "cpu_min_ms": 1000, "cpu_max_ms": 1400},
    Difficulty.MEDIUM: {"rounds": 4, "opponents": 2, "cpu_min_ms": 700,  "cpu_max_ms": 1000},
    Difficulty.HARD:   {"rounds": 5, "opponents": 3, "cpu_min_ms": 450,  "cpu_max_ms": 700},
}

# Tempo humano mais rápido aceito. Abaixo disso é chute ou automação e não ganha bônus.
MIN_HUMAN_REACTION_MS = 150


def config(difficulty: Difficulty) -> dict:
    return dict(DIFFICULTY_CONFIG[difficulty])


def calculate_score(won: int, avg_reaction_ms: float, difficulty: Difficulty) -> int:
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    base = won * 60
    reaction = max(avg_reaction_ms, MIN_HUMAN_REACTION_MS)
    # Bônus de reflexo: até 65 pontos para quem reage perto de 150ms, zero acima de 800ms.
    speed_bonus = max(0, int((800 - reaction) / 10))
    return int((base + speed_bonus) * multipliers[difficulty])
