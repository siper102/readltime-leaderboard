from datetime import datetime

from pydantic import BaseModel


class GameScoreDto(BaseModel):
    score: int
    user_id: int
    created_at: datetime
