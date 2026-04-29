from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.db.base import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)

    mood: Mapped[int] = mapped_column(Integer, nullable=False)
    energy: Mapped[int] = mapped_column(Integer, nullable=False)
    sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    behaviors_json: Mapped[str] = mapped_column(Text, nullable=False)
    wins_json: Mapped[str] = mapped_column(Text, default="[]")
    problems_json: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="uq_daily_log_user_date"),
    )
