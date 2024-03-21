from os import getenv

from dotenv import load_dotenv
from kafka import KafkaConsumer
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from .gamescore_model import Base, GameScore


class GameScorePgConsumer:
    def __init__(self):
        load_dotenv()
        self.session_maker = self.create_session_maker()
        self.consumer = KafkaConsumer(
            getenv("game_score_topic"),
            value_deserializer=GameScore.orm_from_json_string,
            bootstrap_servers=[getenv("kafka_host")],
        )

    def consume(self):
        for message in self.consumer:
            print("[GameScorePgConsumer] Message received")
            self.game_score_pg_consumer(message)

    def game_score_pg_consumer(self, message):
        game_score = message.value
        with self.session_maker.begin() as session:
            session.add(game_score)
            session.commit()
        print("[GameScorePgConsumer] Game score persisted successfully")

    def create_session_maker(self):
        engine = create_engine(self.create_url_from_env())
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine, checkfirst=True)
        return sessionmaker(bind=engine, autoflush=True)

    def create_url_from_env(self):
        return URL.create(
            drivername=getenv("db_drivername"),
            username=getenv("db_username"),
            password=getenv("db_password"),
            host=getenv("db_host"),
            database=getenv("db_database"),
        )
