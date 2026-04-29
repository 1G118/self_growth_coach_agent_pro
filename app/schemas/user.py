from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
