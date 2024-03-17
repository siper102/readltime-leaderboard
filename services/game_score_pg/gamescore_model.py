import json

from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class GameScore(Base):
    __tablename__ = "game_score_redis"
    game_score_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    score = Column(Integer)
    created_at = Column(DateTime)

    @staticmethod
    def orm_from_json_string(json_string: str):
        json_dict = json.loads(json_string)
        return GameScore(**json_dict)
