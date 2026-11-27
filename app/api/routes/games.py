from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.game_session import GameSession, GameType, Difficulty
from app.schemas.game import (
    GameSessionCreate, GameSessionFinish, GameSessionOut,
    MemoryGameConfig, MathQuestion, FaceQuestion, WordQuestion,
)
from app.services import memory_game, math_game, face_game, word_game, difficulty as diff_service

router = APIRouter(prefix="/games", tags=["Jogos"])


# ---------- utilitário ----------
def _get_session_or_404(session_id: int, user: User, db: Session) -> GameSession:
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.user_id == user.id,
    ).first()
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    return session


def _open_session_for_finish(session_id: int, game: GameType, user: User, db: Session) -> GameSession:
    """Sessão do usuário, deste jogo e ainda aberta. Trava a linha para o placar não ser gravado duas vezes."""
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.user_id == user.id,
        GameSession.game_type == game,
    ).with_for_update().first()
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    if session.finished_at is not None:
        raise HTTPException(409, "Este jogo já foi finalizado.")
    return session


def _save_result(session: GameSession, db: Session, score: int, correct: int, total: int, duration: int) -> GameSession:
    session.score = score
    session.correct_answers = correct
    session.total_questions = total
    session.duration_seconds = duration
    session.accuracy = correct / max(total, 1)
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def _elapsed_seconds(session: GameSession) -> int:
    """Duração medida pelo servidor desde o início da sessão. O tempo enviado pelo app não entra no placar."""
    started = session.started_at
    if started is None:
        return 0
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    return max(0, int((datetime.now(timezone.utc) - started).total_seconds()))


def _correct(payload: GameSessionFinish, total: int) -> int:
    """Acertos informados pelo app, limitados ao que é possível neste jogo."""
    return max(0, min(payload.correct_answers, total))


# ---------- sugestão de nível ----------
@router.get("/suggest-difficulty/{game_type}")
def suggest_difficulty(
    game_type: GameType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    suggested = diff_service.suggest_difficulty(current_user.id, game_type, db)
    return {"suggested_difficulty": suggested}


# ---------- MEMÓRIA ----------
@router.post("/memory/start", response_model=MemoryGameConfig)
def start_memory(
    payload: GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = GameSession(
        user_id=current_user.id,
        game_type=GameType.MEMORY,
        difficulty=payload.difficulty,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    board = memory_game.generate_board(payload.difficulty)
    return MemoryGameConfig(session_id=session.id, **board)


@router.post("/memory/finish/{session_id}", response_model=GameSessionOut)
def finish_memory(
    session_id: int,
    payload: GameSessionFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _open_session_for_finish(session_id, GameType.MEMORY, current_user, db)
    cfg = memory_game.DIFFICULTY_CONFIG[session.difficulty]
    total = cfg["pairs"]
    correct = _correct(payload, total)
    duration = _elapsed_seconds(session)
    score = memory_game.calculate_score(
        pairs=total,
        correct_pairs=correct,
        duration_seconds=duration,
        time_limit=cfg["time_limit"],
        difficulty=session.difficulty,
    )
    return _save_result(session, db, score, correct, total, duration)


# ---------- MATEMÁTICA ----------
@router.post("/math/start", response_model=MathQuestion)
def start_math(
    payload: GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = GameSession(
        user_id=current_user.id,
        game_type=GameType.MATH,
        difficulty=payload.difficulty,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    question = math_game.generate_question(payload.difficulty, question_number=1)
    question.pop("answer")  # não envia a resposta pro front
    return MathQuestion(session_id=session.id, **question)


@router.get("/math/question/{session_id}/{question_number}", response_model=MathQuestion)
def get_math_question(
    session_id: int,
    question_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_session_or_404(session_id, current_user, db)
    if session.game_type != GameType.MATH:
        raise HTTPException(404, "Sessão não encontrada")
    question = math_game.generate_question(session.difficulty, question_number)
    question.pop("answer")
    return MathQuestion(session_id=session_id, **question)


@router.post("/math/finish/{session_id}", response_model=GameSessionOut)
def finish_math(
    session_id: int,
    payload: GameSessionFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _open_session_for_finish(session_id, GameType.MATH, current_user, db)
    total = math_game.DIFFICULTY_CONFIG[session.difficulty]["total_questions"]
    correct = _correct(payload, total)
    duration = _elapsed_seconds(session)
    # O tempo médio do app só vale se for coerente com o tempo que o servidor mediu.
    try:
        client_avg = float((payload.metadata or {}).get("avg_response_time", 10))
    except (TypeError, ValueError):
        client_avg = 10.0
    avg_time = max(client_avg, duration / max(total, 1))
    score = math_game.calculate_score(
        correct=correct,
        total=total,
        avg_response_time=avg_time,
        difficulty=session.difficulty,
    )
    return _save_result(session, db, score, correct, total, duration)


# ---------- FAMILIARES ----------
@router.post("/face/start")
def start_face(
    payload: GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        questions = face_game.generate_questions(current_user.id, payload.difficulty, db)
    except ValueError as e:
        raise HTTPException(400, str(e))

    session = GameSession(
        user_id=current_user.id,
        game_type=GameType.FACE,
        difficulty=payload.difficulty,
        total_questions=len(questions),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # remove correct_answer antes de enviar
    safe_questions = [{k: v for k, v in q.items() if k != "correct_answer"} for q in questions]
    return {"session_id": session.id, "questions": safe_questions}


@router.post("/face/finish/{session_id}", response_model=GameSessionOut)
def finish_face(
    session_id: int,
    payload: GameSessionFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _open_session_for_finish(session_id, GameType.FACE, current_user, db)
    total = session.total_questions  # definido pelo servidor no start
    correct = _correct(payload, total)
    score = face_game.calculate_score(correct, total, session.difficulty)
    return _save_result(session, db, score, correct, total, _elapsed_seconds(session))


# ---------- PALAVRAS ----------
@router.post("/word/start")
def start_word(
    payload: GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    questions = word_game.generate_questions(payload.difficulty)
    session = GameSession(
        user_id=current_user.id,
        game_type=GameType.WORD,
        difficulty=payload.difficulty,
        total_questions=len(questions),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # As respostas vão junto para o front conferir cada palavra na hora;
    # o placar final continua sendo calculado aqui no finish.
    return {"session_id": session.id, "questions": questions}


@router.post("/word/finish/{session_id}", response_model=GameSessionOut)
def finish_word(
    session_id: int,
    payload: GameSessionFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _open_session_for_finish(session_id, GameType.WORD, current_user, db)
    total = session.total_questions  # definido pelo servidor no start
    correct = _correct(payload, total)
    score = word_game.calculate_score(correct, total, session.difficulty)
    return _save_result(session, db, score, correct, total, _elapsed_seconds(session))
