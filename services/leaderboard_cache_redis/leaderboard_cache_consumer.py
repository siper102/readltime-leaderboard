from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
from redis import Redis
import json
from os import getenv


class LeaderboardCacheConsumer:

    def __init__(self,):
        self.consumer = KafkaConsumer(
            getenv("leaderboard_change_topic"),
            value_deserializer=lambda d: datetime.fromisoformat(d.decode()).timestamp() * 1000,
            bootstrap_servers=getenv("kafka_host")
        )
        self.producer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            bootstrap_servers=getenv("kafka_host")
        )
        self.redis_obj = Redis(
            host=getenv("redis_host"),
            port=getenv("redis_port"),
            decode_responses=True
        )
        self.duration_ms = 500

    def consume(self):
        for message in self.consumer:
            print("[LeaderboardCacheConsumer] Message received")
            self.leaderboard_cache_consumer(message)

    def leaderboard_cache_consumer(self, message):
        leaderboard_change = message.value
        leader_board_cache = self.redis_obj.get(getenv("redis_cache_key"))
        leader_board_cache = json.loads(leader_board_cache) if leader_board_cache else None
        current_time_ms = datetime.now().timestamp() * 1000
        if not self.can_update_leaderboard(leader_board_cache, current_time_ms):
            print(
                f"[LeaderboardCacheConsumer] Not updating leaderboard for change {leaderboard_change}"
            )
            return
        leader_board = self.redis_obj.zrevrange(name=getenv("redis_game_score_db"), start=0, end=9, withscores=True)
        if not leader_board:
            print("[LeaderboardCacheConsumer] No leaderboard available")
            return
        leader_board_dto = self.map_to_leaderboard_dto(leader_board, current_time_ms)
        
        print(
            "[LeaderboardCacheConsumer] Leaderboard updated in redis cache for change {leaderboard_change}"
        )
        self.redis_obj.set(getenv("redis_cache_key"), json.dumps(leader_board_dto).encode("utf-8"))
        self.producer.send(topic=getenv("leaderboard_topic"), value=leader_board_dto)
        print("[LeaderboardCacheConsumer] Message sent to leaderboard topic")

    def can_update_leaderboard(self, leader_board_cache, current_time_ms) -> bool:
        return (leader_board_cache is None) or (current_time_ms - leader_board_cache.get("current_time_ms") > self.duration_ms)

    def map_to_leaderboard_dto(self, leader_board, current_time_ms) -> dict:
        user_list = []
        for rank, tup in enumerate(leader_board):
            user_id = tup[0]
            user = {
                "rank": rank+1,
                "score": tup[1],
                "nickname": f"user-{int(user_id)}"
            }
            user_list.append(user)
        return {"user_list": user_list, "current_time_ms": current_time_ms}


