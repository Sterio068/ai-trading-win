from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Set

from fastapi import WebSocket

from .metrics import ws_messages_total


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, topic: str, payload: Dict[str, Any]) -> None:
        message = json.dumps({"topic": topic, "payload": payload})
        async with self._lock:
            targets = list(self._connections)
        for connection in targets:
            try:
                await connection.send_text(message)
                ws_messages_total.labels(topic=topic).inc()
            except Exception:
                await self.disconnect(connection)


ws_manager = WebSocketManager()


async def broadcast(topic: str, payload: Dict[str, Any]) -> None:
    await ws_manager.broadcast(topic, payload)


__all__ = ["ws_manager", "broadcast"]
