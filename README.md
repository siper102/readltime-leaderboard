# Realtime Leaderboard
In this project I created a python implementation of the tool that is described in [this article](https://medium.com/@mayilb77/design-a-real-time-leaderboard-system-for-millions-of-users-08b96b4b64ce).
The short description is that a realtime leaderboard should be implemented that expects high data input and needs to show
the latest scores in near real time.
To do this, the data is sent via **Kafka** and is then saved in a **Redis** database. If the leaderboard changes the change is sent
via websocket to allow realtime updates in the user interface.
The implementation in the article is created with Java using the Spring framework.

## The different components:
### Services:
#### 1) Game score service
The code for this service can be found in the file [gamescore_service.py](services%2Fgamescore_service%2Fgamescore_service.py).
In this file the game scores are created. This is done by creating a random user id and a random game score.
By setting the class variable **batch_size** the number of game scores is set and by setting the
variable **sleep_seconds** the time between creating the game scores is set.
By increasing those the amount of user data can be customized.
All the game scores are than published via kafka in the topic named as the value of the environment variable with name **game_score_topic**.

#### 2) Game score redis consumer
The code for this service can be found in the file [game_score_redis_consumer.py](services%2Fgame_score_redis%2Fgame_score_redis_consumer.py).
In this service the scores published by the game scores service are consumed and saved in a **Redis sorted set** which will make extracting the top 10 players faster.
After saving an message is sent that the score was updated so the leaderboard cache can cache the newest top 10 players.

#### 3) Game score Postgres service
This Service just receives the messages sent by the game score service and saves them into a postgres
database. The inserts are performed by **SQLAlchemy**. The scores are saved in a relational database for analytical purposes.
The code can be found in [gamescore_model.py](services%2Fgame_score_pg%2Fgamescore_model.py).

#### 4) Leaderboard cache service
In this services the current top 10 players are saved in a **Redis key-value store**.
Each time the redis consumer service saves a new game score a message is sent to this service via kafka with the current timestamp.
When this message is consumed by this service it selects the latest top 10 players from the sorted set and saves the resulting string with the current timestamp in a redis database.
Furthermore, the latest top 10 players are sent via kafka to the frontend.
To avoid overhead this procedure is just performed every 500ms.


### Controller
In this package the frontend is defined. The frontend is build with **FastAPI**. The leaderboard is consumed with kafka
an is then broadcasted with a websocket. When someone connects to the leaderboard he automatically connects to the websocket and receives
realtime updates.

## How to start the app on a local machine
First we need to start kafka, redis and postgres. This is done by docker and they can be started with
```shell
docker-compose up
```
This starts zookeeper and kafka as well as redis and postgres. Furthermore, it creates all the
kafka topics.
After the containers are running we need to install the python dependencies that are defined in the requirements.txt file.
So just start a python environment and run
```shell
pip install -r requirements.txt
```
Before starting the service the environment variables need to be saved in a .env file.
Create a file named .env in /services with the following content:
```.text
db_drivername=postgresql+psycopg2
db_username=root
db_password=pw123
db_host=localhost
db_database=realtime-game-board
kafka_host=localhost
game_score_topic=game-score
leaderboard_topic=leaderboard
leaderboard_change_topic=leaderboard-change
redis_host=localhost
redis_port=6379
redis_game_score_db=game-score
redis_cache_key=game-score-cache
```
and one in /controller with content
```text
kafka_host=localhost
leaderboard_topic=leaderboard
```
Then start the services:
```shell
python services/main.py
```
In another shell window start the web service:
```shell
cd controller
uvicorn main:app --reload
```
Then just visit http://localhost:8000.
