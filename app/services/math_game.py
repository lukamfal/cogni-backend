import random
from app.models.game_session import Difficulty

DIFFICULTY_CONFIG = {
    Difficulty.EASY: {
        "operations": ["add", "sub"],
        "max_num": 10,
        "total_questions": 5,
        "time_per_question": 20,
    },
    Difficulty.MEDIUM: {
        "operations": ["add", "sub", "mul"],
        "max_num": 20,
        "total_questions": 8,
        "time_per_question": 15,
    },
    Difficulty.HARD: {
        "operations": ["add", "sub", "mul", "div"],
        "max_num": 50,
        "total_questions": 10,
        "time_per_question": 10,
    },
}


def generate_question(difficulty: Difficulty, question_number: int) -> dict:
    cfg = DIFFICULTY_CONFIG[difficulty]
    op = random.choice(cfg["operations"])
    a = random.randint(1, cfg["max_num"])
    b = random.randint(1, cfg["max_num"])

    if op == "add":
        expression, answer = f"{a} + {b}", a + b
    elif op == "sub":
        a, b = max(a, b), min(a, b)
        expression, answer = f"{a} - {b}", a - b
    elif op == "mul":
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        expression, answer = f"{a} × {b}", a * b
    else:  # div
        b = random.randint(1, 10)
        a = b * random.randint(1, 10)
        expression, answer = f"{a} ÷ {b}", a // b

    options = _generate_options(answer)

    return {
        "question_number": question_number,
        "total_questions": cfg["total_questions"],
        "expression": expression,
        "answer": answer,
        "options": options,
        "time_limit_seconds": cfg["time_per_question"],
    }


def _generate_options(correct: int) -> list[int]:
    """4 alternativas onde uma é a correta."""
    options = {correct}
    while len(options) < 4:
        delta = random.randint(1, 5)
        options.add(correct + random.choice([-delta, delta]))
    result = list(options)
    random.shuffle(result)
    return result


def calculate_score(
    correct: int,
    total: int,
    avg_response_time: float,
    difficulty: Difficulty,
) -> int:
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    base = correct * 40
    speed_bonus = max(0, int((10 - avg_response_time) * 5)) if avg_response_time < 10 else 0
    return int((base + speed_bonus) * multipliers[difficulty])
