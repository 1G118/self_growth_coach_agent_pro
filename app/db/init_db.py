from app.db.base import Base
from app.db.session import engine

from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.goal import Goal
from app.models.reflection import Reflection
from app.models.memory import Memory


def init_db():
    Base.metadata.create_all(bind=engine)
