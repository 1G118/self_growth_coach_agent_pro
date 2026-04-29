from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.prompts.coach_prompts import WEEKLY_REVIEW_PROMPT
from app.services.llm_service import call_llm_json
from app.services.memory_service import get_memories
from app.services.goal_service import get_active_goals
from app.services.reflection_service import get_recent_logs, serialize_log, serialize_goal


def run_weekly_review(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recent_logs = get_recent_logs(db, user_id, 7)
    if not recent_logs:
        raise HTTPException(status_code=404, detail="No logs found")

    active_goals = get_active_goals(db, user_id)
    memories = get_memories(db, user_id)

    payload = {
        "user": {
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
        },
        "recent_logs": [serialize_log(x) for x in recent_logs],
        "active_goals": [serialize_goal(x) for x in active_goals],
        "memories": memories,
    }

    return call_llm_json(WEEKLY_REVIEW_PROMPT, payload)
