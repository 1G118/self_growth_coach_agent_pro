from pydantic import BaseModel, Field
from datetime import date


class DailyLogCreate(BaseModel):
    user_id: int
    log_date: date = Field(default_factory=date.today)
    mood: int = Field(..., ge=1, le=10)
    energy: int = Field(..., ge=1, le=10)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    behaviors: list[str]
    wins: list[str] = []
    problems: list[str] = []
    notes: str | None = None


class DailyLogOut(BaseModel):
    id: int
    user_id: int
    log_date: date
    mood: int
    energy: int
    sleep_hours: float | None
    behaviors: list[str]
    wins: list[str]
    problems: list[str]
    notes: str | None
