from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate
from app.services.goal_service import get_active_goals

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("")
def create_goal(data: GoalCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = Goal(
        user_id=data.user_id,
        title=data.title,
        why=data.why,
        metric=data.metric,
        target_date=data.target_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.patch("/{goal_id}")
def update_goal(goal_id: int, data: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.progress = data.progress
    goal.status = data.status
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{user_id}/active")
def active_goals(user_id: int, db: Session = Depends(get_db)):
    return get_active_goals(db, user_id)
