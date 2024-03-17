from os import getenv

from aiokafka import AIOKafkaConsumer
from connection_manager import ConnectionManager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")

load_dotenv()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Asynchronous Kafka
consumer = AIOKafkaConsumer(
    getenv("leaderboard_topic"),
    bootstrap_servers=getenv("kafka_host"),
    value_deserializer=lambda v: v.decode("utf-8"),
)


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="leaderboard.html")


@app.websocket("/live-updates/leaderboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await consumer.start()
            try:
                async for message in consumer:
                    print(f"Message {message} received")
                    await manager.broadcast(message)
            finally:
                print("Stopping kafka consumer")
                await consumer.stop()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
