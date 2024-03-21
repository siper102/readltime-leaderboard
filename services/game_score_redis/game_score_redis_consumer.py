import json
from os import getenv

from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer
from redis import Redis


class GameScoreRedisConsumer:
    load_dotenv()
    consumer = KafkaConsumer(
        getenv("game_score_topic"),
        value_deserializer=json.loads,
        bootstrap_servers=[getenv("kafka_host")],
    )
    producer = KafkaProducer(
        value_serializer=lambda i: str(i).encode("utf-8"),
        bootstrap_servers=[getenv("kafka_host")],
    )
    redis_obj = Redis(
        host=getenv("redis_host"), port=getenv("redis_port"), decode_responses=True
    )

    def consume(self):
        for message in self.consumer:
            print("[GameScoreRedisConsumer] Message received")
            self.game_score_redis_consumer(message=message)

    def game_score_redis_consumer(self, message):
        score_dto = message.value
        self.redis_obj.zincrby(
            name=getenv("redis_game_score_db"),
            amount=score_dto.get("score"),
            value=str(score_dto.get("user_id")),
        )
        print("[GameScoreRedisConsumer] Game score saved in Redis")
        self.producer.send(
            topic=getenv("leaderboard_change_topic"), value=score_dto.get("created_at")
        )
        print("[GameScoreRedisConsumer] Message sent to topic leaderboard-change")
