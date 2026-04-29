from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    memory_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        UniqueConstraint("user_id", "memory_type", name="uq_memory_user_type"),
    )
