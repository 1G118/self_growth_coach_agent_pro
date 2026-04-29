from datetime import datetime
from sqlalchemy.orm import Session

from app.models.memory import Memory


def get_memories(db: Session, user_id: int) -> dict[str, str]:
    rows = db.query(Memory).filter(Memory.user_id == user_id).all()
    return {row.memory_type: row.content for row in rows}


def upsert_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    content: str,
    confidence: float = 0.8,
):
    memory = (
        db.query(Memory)
        .filter(Memory.user_id == user_id, Memory.memory_type == memory_type)
        .first()
    )

    if memory:
        memory.content = content
        memory.confidence = confidence
        memory.updated_at = datetime.utcnow()
    else:
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            confidence=confidence,
            updated_at=datetime.utcnow(),
        )
        db.add(memory)

    db.commit()
    db.refresh(memory)
    return memory


def apply_memory_updates(db: Session, user_id: int, memory_updates: dict):
    if not isinstance(memory_updates, dict):
        return

    for key, value in memory_updates.items():
        if isinstance(value, str) and value.strip():
            upsert_memory(db, user_id, key, value.strip())
