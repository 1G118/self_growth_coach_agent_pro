from pydantic import BaseModel


class DailyReviewRequest(BaseModel):
    log_date: str | None = None
