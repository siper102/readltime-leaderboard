from pydantic import BaseModel
from datetime import datetime


class GameScoreDto(BaseModel):
    score: int
    user_id: int
    created_at: datetime
