from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reflection import DailyReviewRequest
from app.services.reflection_service import run_daily_review
from app.services.weekly_service import run_weekly_review

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/daily-review/{user_id}")
def daily_review(
    user_id: int,
    data: DailyReviewRequest | None = None,
    db: Session = Depends(get_db),
):
    target_date = date.today()
    if data and data.log_date:
        target_date = date.fromisoformat(data.log_date)

    return run_daily_review(db, user_id, target_date)


@router.post("/weekly-review/{user_id}")
def weekly_review(user_id: int, db: Session = Depends(get_db)):
    return run_weekly_review(db, user_id)
