from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.daily_log import DailyLog
from app.services.goal_service import get_active_goals
from app.services.memory_service import get_memories
from app.services.reflection_service import serialize_log

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{user_id}")
def dashboard(user_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id)
        .order_by(DailyLog.log_date.desc())
        .limit(14)
        .all()
    )

    avg_mood = round(sum(x.mood for x in logs) / len(logs), 2) if logs else None
    avg_energy = round(sum(x.energy for x in logs) / len(logs), 2) if logs else None

    active_goals = get_active_goals(db, user_id)

    return {
        "days_logged": len(logs),
        "avg_mood": avg_mood,
        "avg_energy": avg_energy,
        "active_goal_count": len(active_goals),
        "active_goals": active_goals,
        "memories": get_memories(db, user_id),
        "recent_logs": [serialize_log(x) for x in logs[:5]],
    }
