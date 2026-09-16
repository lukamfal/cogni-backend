import random
from app.models.game_session import Difficulty

# Banco de palavras com dica (pode ser expandido ou vir de um DB)
WORD_BANK = [
    {"word": "CASA",    "hint": "Lugar onde moramos"},
    {"word": "PRATO",   "hint": "Usamos para comer"},
    {"word": "FLOR",    "hint": "Nasce no jardim"},
    {"word": "CARRO",   "hint": "Meio de transporte"},
    {"word": "LIVRO",   "hint": "Gostamos de ler"},
    {"word": "AGUA",    "hint": "Bebemos todo dia"},
    {"word": "PORTA",   "hint": "Abrimos para entrar"},
    {"word": "JANELA",  "hint": "Deixa a luz entrar"},
    {"word": "ARVORE",  "hint": "Tem folhas e galhos"},
    {"word": "CADEIRA", "hint": "Usamos para sentar"},
    {"word": "MESA",    "hint": "Comemos sobre ela"},
    {"word": "CAMA",    "hint": "Dormimos nela"},
    {"word": "FOGAO",   "hint": "Cozinhamos nele"},
    {"word": "JARDIM",  "hint": "Cheio de plantas"},
    {"word": "MUSICA",  "hint": "Ouvimos com alegria"},
]

DIFFICULTY_CONFIG = {
    Difficulty.EASY:   {"hidden_letters": 1, "total_questions": 5,  "time_per_question": 30, "show_hint": True},
    Difficulty.MEDIUM: {"hidden_letters": 2, "total_questions": 7,  "time_per_question": 20, "show_hint": True},
    Difficulty.HARD:   {"hidden_letters": 3, "total_questions": 10, "time_per_question": 15, "show_hint": False},
}


def _mask_word(word: str, n_hidden: int) -> tuple[str, list[str]]:
    """Retorna a palavra mascarada e as letras corretas escondidas."""
    indices = random.sample(range(len(word)), min(n_hidden, len(word)))
    masked = list(word)
    hidden = []
    for i in indices:
        hidden.append(word[i])
        masked[i] = "_"
    return "".join(masked), hidden


def generate_questions(difficulty: Difficulty) -> list[dict]:
    cfg = DIFFICULTY_CONFIG[difficulty]
    sample = random.sample(WORD_BANK, cfg["total_questions"])
    questions = []

    for i, entry in enumerate(sample):
        masked, hidden = _mask_word(entry["word"], cfg["hidden_letters"])

        # opções de letras: corretas + distratores
        alphabet = "ABCDEFGHIJKLMNOPRSTUVZ"
        distractors = random.sample(
            [c for c in alphabet if c not in hidden], k=max(0, 4 - len(hidden))
        )
        options = hidden + distractors
        random.shuffle(options)

        questions.append({
            "question_number": i + 1,
            "total_questions": cfg["total_questions"],
            "masked_word": masked,
            "hint": entry["hint"] if cfg["show_hint"] else "",
            "correct_letters": hidden,
            "options": options,
            "full_word": entry["word"],
            "time_limit_seconds": cfg["time_per_question"],
        })

    return questions


def calculate_score(correct: int, total: int, difficulty: Difficulty) -> int:
    multipliers = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1.5, Difficulty.HARD: 2}
    return int(correct * 45 * multipliers[difficulty])
