import logging

from fastapi import WebSocket


class ConnectionManager:
    """
    Handle all websocket connections here
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"Accepted connection from {websocket}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.logger.debug(f"Disconnected from {websocket}")

    async def broadcast(self, message: str):
        self.logger.debug(
            f"Broadcasting message to {len(self.active_connections)} clients"
        )
        for connection in self.active_connections:
            await connection.send_text(message)
