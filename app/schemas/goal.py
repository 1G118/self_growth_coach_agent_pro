from pydantic import BaseModel, Field
from datetime import date, timedelta


class GoalCreate(BaseModel):
    user_id: int
    title: str
    why: str | None = None
    metric: str | None = None
    target_date: date = Field(default_factory=lambda: date.today() + timedelta(days=1))


class GoalUpdate(BaseModel):
    progress: int = Field(..., ge=0, le=100)
    status: str = Field("active", pattern="^(active|done|failed|paused)$")
