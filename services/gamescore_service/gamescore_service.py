from kafka import KafkaProducer
from datetime import datetime
from random import randint
from .gamescore_dto import GameScoreDto
import time
from os import getenv


class GameScoreService:

    def __init__(self,sleep_seconds, batch_size):
        self.sleep_seconds = sleep_seconds
        self.batch_size = batch_size
        self.producer = KafkaProducer(
            key_serializer=lambda i: str(i).encode("utf-8"),
            value_serializer=lambda d: d.model_dump_json().encode("utf-8"),
            bootstrap_servers=getenv("kafka_host")
        )

    def produce(self):
        while True:
            self.random_game_scores()
            time.sleep(self.sleep_seconds)

    def random_game_scores(self):
        for _ in range(self.batch_size):
            self.publish_game_score()

    def publish_game_score(self):
        game_score_dto = self.build_game_score()
        self.producer.send(
            topic=getenv("game_score_topic"),
            key=game_score_dto.user_id,
            value=game_score_dto
        )
        print(
            f"[GameScoreService] score from user {game_score_dto.user_id} published to {getenv('game_score_topic')}"
        )

    def build_game_score(self) -> GameScoreDto:
        return GameScoreDto(
            score=randint(a=1, b=100),
            user_id=randint(a=1, b=10),
            created_at=datetime.now()
        )




