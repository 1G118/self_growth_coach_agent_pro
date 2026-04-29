from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.services.memory_service import get_memories
from app.services.goal_service import get_active_goals

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = User(name=data.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at,
        "memories": get_memories(db, user_id),
        "active_goals": get_active_goals(db, user_id),
    }
