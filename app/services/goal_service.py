from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.goal import Goal


def get_active_goals(db: Session, user_id: int) -> list[Goal]:
    return (
        db.query(Goal)
        .filter(Goal.user_id == user_id, Goal.status == "active")
        .order_by(Goal.target_date.asc(), Goal.id.asc())
        .all()
    )


def create_goal_from_agent(
    db: Session,
    user_id: int,
    title: str,
    why: str | None,
    metric: str | None,
    target_date: date | None = None,
):
    goal = Goal(
        user_id=user_id,
        title=title,
        why=why,
        metric=metric,
        target_date=target_date or date.today() + timedelta(days=1),
        status="active",
        progress=0,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def create_tomorrow_goals(db: Session, user_id: int, goals: list[dict], base_date: date):
    for item in goals:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue

        create_goal_from_agent(
            db=db,
            user_id=user_id,
            title=title,
            why=item.get("why"),
            metric=item.get("metric"),
            target_date=base_date + timedelta(days=1),
        )
