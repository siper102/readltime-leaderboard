from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime, BigInteger
import json

Base = declarative_base()


class GameScore(Base):
    __tablename__ = "game_score_redis"
    game_score_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    score = Column(Integer)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<GameScore(user_id={self.user_id}, score={self.score}, created_at={self.created_at})>"

    @staticmethod
    def orm_from_json_string(json_string: str):
        json_dict = json.loads(json_string)
        return GameScore(**json_dict)
