from sqlalchemy.orm import Session
from app.models.game_session import GameSession, GameType, Difficulty


def suggest_difficulty(user_id: int, game_type: GameType, db: Session) -> Difficulty:
    """
    Analisa as últimas 5 sessões do jogo e sugere a dificuldade ideal.
    - Acurácia > 85% → sobe o nível
    - Acurácia < 50% → desce o nível
    - Entre 50% e 85% → mantém
    """
    recent = (
        db.query(GameSession)
        .filter(
            GameSession.user_id == user_id,
            GameSession.game_type == game_type,
            GameSession.finished_at.isnot(None),  # jogos abandonados não contam
        )
        .order_by(GameSession.started_at.desc())
        .limit(5)
        .all()
    )

    if not recent:
        return Difficulty.EASY

    avg_accuracy = sum(s.accuracy for s in recent) / len(recent)
    current_diff = recent[0].difficulty

    if avg_accuracy > 0.85:
        return _bump_up(current_diff)
    elif avg_accuracy < 0.50:
        return _bump_down(current_diff)
    return current_diff


def _bump_up(d: Difficulty) -> Difficulty:
    order = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    idx = order.index(d)
    return order[min(idx + 1, len(order) - 1)]


def _bump_down(d: Difficulty) -> Difficulty:
    order = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    idx = order.index(d)
    return order[max(idx - 1, 0)]
