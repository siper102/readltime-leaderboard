from game_score_redis.game_score_redis_consumer import GameScoreRedisConsumer
from leaderboard_cache_redis.leaderboard_cache_consumer import LeaderboardCacheConsumer
from gamescore_service.gamescore_service import GameScoreService
from game_score_pg.game_score_pg_consumer import GameScorePgConsumer
from threading import Thread
from dotenv import load_dotenv


def main():
    game_score_redis = GameScoreRedisConsumer()
    leaderboard_cache = LeaderboardCacheConsumer()
    game_score_service = GameScoreService(batch_size=5, sleep_seconds=1)
    game_score_pg = GameScorePgConsumer()

    consumer1_thread = Thread(target=game_score_redis.consume, args=())
    consumer2_thread = Thread(target=leaderboard_cache.consume, args=())
    consumer3_thread = Thread(target=game_score_pg.consume, args=())
    producer_thread = Thread(target=game_score_service.produce, args=())

    producer_thread.start()
    consumer1_thread.start()
    consumer2_thread.start()
    consumer3_thread.start()


if __name__ == "__main__":
    load_dotenv()
    main()
