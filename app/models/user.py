from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    logs = relationship("DailyLog", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    reflections = relationship("Reflection", back_populates="user")
    memories = relationship("Memory", back_populates="user")
