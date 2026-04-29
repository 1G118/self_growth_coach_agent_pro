from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.db.base import Base


class Reflection(Base):
    __tablename__ = "reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    pattern_analysis_json: Mapped[str] = mapped_column(Text, default="[]")
    advice_json: Mapped[str] = mapped_column(Text, default="[]")
    tomorrow_goals_json: Mapped[str] = mapped_column(Text, default="[]")
    risk_alerts_json: Mapped[str] = mapped_column(Text, default="[]")
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reflections")

    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="uq_reflection_user_date"),
    )
