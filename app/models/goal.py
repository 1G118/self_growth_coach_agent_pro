from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.db.base import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    why: Mapped[str | None] = mapped_column(Text, nullable=True)
    metric: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(String(30), default="active")
    progress: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")
