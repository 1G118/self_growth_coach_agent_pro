import json
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.reflection import Reflection
from app.prompts.coach_prompts import DAILY_REVIEW_PROMPT
from app.services.llm_service import call_llm_json
from app.services.memory_service import get_memories, apply_memory_updates
from app.services.goal_service import get_active_goals, create_tomorrow_goals


def serialize_log(log: DailyLog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "log_date": log.log_date.isoformat(),
        "mood": log.mood,
        "energy": log.energy,
        "sleep_hours": log.sleep_hours,
        "behaviors": json.loads(log.behaviors_json),
        "wins": json.loads(log.wins_json or "[]"),
        "problems": json.loads(log.problems_json or "[]"),
        "notes": log.notes,
    }


def serialize_goal(goal) -> dict:
    return {
        "id": goal.id,
        "title": goal.title,
        "why": goal.why,
        "metric": goal.metric,
        "target_date": goal.target_date.isoformat(),
        "status": goal.status,
        "progress": goal.progress,
    }


def get_recent_logs(db: Session, user_id: int, limit: int = 7) -> list[DailyLog]:
    return (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id)
        .order_by(DailyLog.log_date.desc())
        .limit(limit)
        .all()
    )


def run_daily_review(db: Session, user_id: int, target_date: date) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today_log = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id, DailyLog.log_date == target_date)
        .first()
    )
    if not today_log:
        raise HTTPException(status_code=404, detail="No daily log found for this date")

    recent_logs = get_recent_logs(db, user_id, 7)
    active_goals = get_active_goals(db, user_id)
    memories = get_memories(db, user_id)

    payload = {
        "user": {
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
        },
        "today_log": serialize_log(today_log),
        "recent_logs": [serialize_log(x) for x in recent_logs],
        "active_goals": [serialize_goal(x) for x in active_goals],
        "memories": memories,
    }

    result = call_llm_json(DAILY_REVIEW_PROMPT, payload)

    apply_memory_updates(db, user_id, result.get("memory_updates", {}))
    create_tomorrow_goals(
        db=db,
        user_id=user_id,
        goals=result.get("tomorrow_goals", []),
        base_date=target_date,
    )

    reflection = (
        db.query(Reflection)
        .filter(Reflection.user_id == user_id, Reflection.log_date == target_date)
        .first()
    )

    if not reflection:
        reflection = Reflection(
            user_id=user_id,
            log_date=target_date,
            summary=result.get("summary", ""),
            pattern_analysis_json=json.dumps(result.get("pattern_analysis", []), ensure_ascii=False),
            advice_json=json.dumps(result.get("advice", []), ensure_ascii=False),
            tomorrow_goals_json=json.dumps(result.get("tomorrow_goals", []), ensure_ascii=False),
            risk_alerts_json=json.dumps(result.get("risk_alerts", []), ensure_ascii=False),
            raw_json=json.dumps(result, ensure_ascii=False),
        )
        db.add(reflection)
    else:
        reflection.summary = result.get("summary", "")
        reflection.pattern_analysis_json = json.dumps(result.get("pattern_analysis", []), ensure_ascii=False)
        reflection.advice_json = json.dumps(result.get("advice", []), ensure_ascii=False)
        reflection.tomorrow_goals_json = json.dumps(result.get("tomorrow_goals", []), ensure_ascii=False)
        reflection.risk_alerts_json = json.dumps(result.get("risk_alerts", []), ensure_ascii=False)
        reflection.raw_json = json.dumps(result, ensure_ascii=False)

    db.commit()
    return result
