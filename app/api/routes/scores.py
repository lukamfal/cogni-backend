from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.game_session import GameSession, GameType, Difficulty
from app.schemas.game import GameSessionOut

router = APIRouter(prefix="/scores", tags=["Pontuações"])


@router.get("/history", response_model=list[GameSessionOut])
def history(
    game_type: GameType | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(GameSession).filter(
        GameSession.user_id == current_user.id,
        GameSession.finished_at.isnot(None),
    )
    if game_type:
        q = q.filter(GameSession.game_type == game_type)
    return q.order_by(GameSession.finished_at.desc()).limit(limit).all()


@router.get("/best")
def best_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna o melhor score do usuário por jogo + dificuldade."""
    sessions = db.query(GameSession).filter(
        GameSession.user_id == current_user.id,
        GameSession.finished_at.isnot(None),
    ).all()

    best = {}
    for s in sessions:
        key = f"{s.game_type.value}_{s.difficulty.value}"
        if key not in best or s.score > best[key]["score"]:
            best[key] = {
                "game_type": s.game_type,
                "difficulty": s.difficulty,
                "score": s.score,
                "accuracy": s.accuracy,
            }
    return list(best.values())


@router.get("/summary")
def summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resumo geral: streak, total de sessões, pontos acumulados."""
    from sqlalchemy import func
    from datetime import date, timedelta

    sessions = db.query(GameSession).filter(
        GameSession.user_id == current_user.id,
        GameSession.finished_at.isnot(None),
    ).order_by(GameSession.finished_at.desc()).all()

    total_points = sum(s.score for s in sessions)
    total_sessions = len(sessions)

    # calcula streak de dias consecutivos
    played_days = sorted({s.finished_at.date() for s in sessions}, reverse=True)
    streak = 0
    today = date.today()
    for i, d in enumerate(played_days):
        if d == today - timedelta(days=i):
            streak += 1
        else:
            break

    return {
        "total_sessions": total_sessions,
        "total_points": total_points,
        "streak_days": streak,
    }
