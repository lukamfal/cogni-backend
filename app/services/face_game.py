import random
from sqlalchemy.orm import Session
from app.models.family_member import FamilyMember
from app.models.game_session import Difficulty

DIFFICULTY_CONFIG = {
    Difficulty.EASY:   {"options_count": 2, "total_questions": 4, "time_per_question": 30},
    Difficulty.MEDIUM: {"options_count": 4, "total_questions": 6, "time_per_question": 20},
    Difficulty.HARD:   {"options_count": 6, "total_questions": 8, "time_per_question": 15},
}


def generate_questions(user_id: int, difficulty: Difficulty, db: Session) -> list[dict]:
    """
    Gera rodadas do jogo de reconhecimento de familiares.
    Cada rodada: mostra uma foto + N nomes para escolher.
    """
    cfg = DIFFICULTY_CONFIG[difficulty]
    members = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id,
        FamilyMember.photo_url.isnot(None),
    ).all()

    if len(members) < cfg["options_count"]:
        raise ValueError(
            f"Cadastre ao menos {cfg['options_count']} familiares com foto para este nível."
        )

    questions = []
    sample = random.sample(members, min(cfg["total_questions"], len(members)))

    for i, correct_member in enumerate(sample):
        distractors = [m for m in members if m.id != correct_member.id]
        distractors = random.sample(distractors, cfg["options_count"] - 1)
        options = [m.name for m in distractors] + [correct_member.name]
        random.shuffle(options)

        questions.append({
            "question_number": i + 1,
            "total_questions": len(sample),
            "family_member_id": correct_member.id,
            "photo_url": correct_member.photo_url,
            "options": options,
            "correct_answer": correct_member.name,
            "time_limit_seconds": cfg["time_per_question"],
        })

    return questions


def calculate_score(correct: int, total: int, difficulty: Difficulty) -> int:
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    return int(correct * 60 * multipliers[difficulty])
