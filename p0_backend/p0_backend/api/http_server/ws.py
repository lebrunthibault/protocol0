""" websocket endpoint for broadcasting the song state """
import json
from enum import Enum
from typing import List

from fastapi import APIRouter
from loguru import logger
from starlette.websockets import WebSocket, WebSocketDisconnect

from p0_backend.lib.ableton.ableton_set.server_state import get_favorite_device_names

ws_router = APIRouter()

_DEBUG = False


class WebSocketPayloadType(Enum):
    FAVORITE_DEVICES = "FAVORITE_DEVICES"


class WebSocketManager:
    def __init__(self):
        self._active_connections: List[WebSocket] = []

    def __repr__(self) -> str:
        return f"{len(self._active_connections)} active connections"

    @property
    def active_connections(self) -> List[WebSocket]:
        return self._active_connections

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active_connections.append(websocket)
        if _DEBUG:
            logger.info(f"connection added: {self}")

        await self._broadcast_data(
            WebSocketPayloadType.FAVORITE_DEVICES, get_favorite_device_names()
        )

    def disconnect(self, websocket: WebSocket):
        self._active_connections.remove(websocket)

    async def _broadcast_data(self, payload_type: WebSocketPayloadType, data_json: str):
        for connection in self._active_connections:
            await connection.send_text(json.dumps({"type": payload_type.value, "data": data_json}))


ws_manager = WebSocketManager()


@ws_router.get("/ws/connections")
async def get_connections():
    return [ws.client for ws in ws_manager.active_connections]


@ws_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if _DEBUG:
                logger.info(f"Received song state data: {data}")
    except WebSocketDisconnect:
        pass

    ws_manager.disconnect(websocket)
