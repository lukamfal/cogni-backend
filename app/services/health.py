from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from collections import Counter
from typing import Optional

from app.models.health import HealthLog, Mood
from app.schemas.health import HealthLogCreate, HealthLogUpdate, HealthSummary


def get_log_by_date(db: Session, user_id: int, log_date: date) -> Optional[HealthLog]:
    return db.query(HealthLog).filter(
        HealthLog.user_id == user_id,
        HealthLog.log_date == log_date,
    ).first()


def upsert_log(db: Session, user_id: int, data: HealthLogCreate) -> HealthLog:
    """Cria ou atualiza o registro do dia."""
    existing = get_log_by_date(db, user_id, data.log_date)
    if existing:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    log = HealthLog(user_id=user_id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_log(db: Session, log: HealthLog, data: HealthLogUpdate) -> HealthLog:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


def get_history(db: Session, user_id: int, days: int = 30) -> list[HealthLog]:
    since = date.today() - timedelta(days=days)
    return db.query(HealthLog).filter(
        HealthLog.user_id == user_id,
        HealthLog.log_date >= since,
    ).order_by(HealthLog.log_date.desc()).all()


def get_weekly_summary(db: Session, user_id: int) -> HealthSummary:
    logs = get_history(db, user_id, days=7)
    if not logs:
        return HealthSummary(
            avg_water_cups=0, avg_sleep_hours=0, avg_steps=0,
            avg_exercise_minutes=0, medication_adherence=0,
            most_common_mood=None, logs_this_week=0,
        )

    n = len(logs)
    moods = [l.mood for l in logs if l.mood]
    most_common_mood = Counter(moods).most_common(1)[0][0] if moods else None
    med_taken = sum(1 for l in logs if l.medication_taken)

    return HealthSummary(
        avg_water_cups=round(sum(l.water_cups for l in logs) / n, 1),
        avg_sleep_hours=round(sum(l.sleep_hours for l in logs) / n, 1),
        avg_steps=round(sum(l.steps for l in logs) / n),
        avg_exercise_minutes=round(sum(l.exercise_minutes for l in logs) / n, 1),
        medication_adherence=round(med_taken / n, 2),
        most_common_mood=most_common_mood,
        logs_this_week=n,
    )
