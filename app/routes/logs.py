import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.daily_log import DailyLog
from app.schemas.daily_log import DailyLogCreate
from app.services.reflection_service import serialize_log

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("")
def create_or_update_log(data: DailyLogCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == data.user_id, DailyLog.log_date == data.log_date)
        .first()
    )

    if not log:
        log = DailyLog(
            user_id=data.user_id,
            log_date=data.log_date,
            mood=data.mood,
            energy=data.energy,
            sleep_hours=data.sleep_hours,
            behaviors_json=json.dumps(data.behaviors, ensure_ascii=False),
            wins_json=json.dumps(data.wins, ensure_ascii=False),
            problems_json=json.dumps(data.problems, ensure_ascii=False),
            notes=data.notes,
        )
        db.add(log)
    else:
        log.mood = data.mood
        log.energy = data.energy
        log.sleep_hours = data.sleep_hours
        log.behaviors_json = json.dumps(data.behaviors, ensure_ascii=False)
        log.wins_json = json.dumps(data.wins, ensure_ascii=False)
        log.problems_json = json.dumps(data.problems, ensure_ascii=False)
        log.notes = data.notes

    db.commit()
    db.refresh(log)

    return {
        "ok": True,
        "log": serialize_log(log),
    }


@router.get("/{user_id}")
def list_logs(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id)
        .order_by(DailyLog.log_date.desc())
        .limit(limit)
        .all()
    )
    return [serialize_log(x) for x in logs]
