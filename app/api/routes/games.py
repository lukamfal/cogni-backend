from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
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
    session = _get_session_or_404(session_id, current_user, db)
    cfg = memory_game.DIFFICULTY_CONFIG[session.difficulty]
    score = memory_game.calculate_score(
        pairs=cfg["pairs"],
        correct_pairs=payload.correct_answers,
        duration_seconds=payload.duration_seconds,
        time_limit=cfg["time_limit"],
        difficulty=session.difficulty,
    )
    session.score = score
    session.correct_answers = payload.correct_answers
    session.total_questions = payload.total_questions
    session.duration_seconds = payload.duration_seconds
    session.accuracy = payload.correct_answers / max(payload.total_questions, 1)
    session.finished_at = datetime.utcnow()
    session.metadata = payload.metadata or {}
    db.commit()
    db.refresh(session)
    return session


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
    session = _get_session_or_404(session_id, current_user, db)
    avg_time = payload.metadata.get("avg_response_time", 10)
    score = math_game.calculate_score(
        correct=payload.correct_answers,
        total=payload.total_questions,
        avg_response_time=avg_time,
        difficulty=session.difficulty,
    )
    session.score = score
    session.correct_answers = payload.correct_answers
    session.total_questions = payload.total_questions
    session.duration_seconds = payload.duration_seconds
    session.accuracy = payload.correct_answers / max(payload.total_questions, 1)
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


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
    session = _get_session_or_404(session_id, current_user, db)
    score = face_game.calculate_score(payload.correct_answers, payload.total_questions, session.difficulty)
    session.score = score
    session.correct_answers = payload.correct_answers
    session.total_questions = payload.total_questions
    session.duration_seconds = payload.duration_seconds
    session.accuracy = payload.correct_answers / max(payload.total_questions, 1)
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


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

    safe_questions = [{k: v for k, v in q.items() if k not in ("correct_letters", "full_word")} for q in questions]
    return {"session_id": session.id, "questions": safe_questions}


@router.post("/word/finish/{session_id}", response_model=GameSessionOut)
def finish_word(
    session_id: int,
    payload: GameSessionFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_session_or_404(session_id, current_user, db)
    score = word_game.calculate_score(payload.correct_answers, payload.total_questions, session.difficulty)
    session.score = score
    session.correct_answers = payload.correct_answers
    session.total_questions = payload.total_questions
    session.duration_seconds = payload.duration_seconds
    session.accuracy = payload.correct_answers / max(payload.total_questions, 1)
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session
