from __future__ import annotations

import asyncio
from typing import Dict, Set

from fastapi import WebSocket

from .metrics import WS_BROADCAST_COUNTER


class WebSocketHub:
    def __init__(self) -> None:
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def register(self, channel: str, websocket: WebSocket) -> None:
        async with self.lock:
            self.connections.setdefault(channel, set()).add(websocket)

    async def unregister(self, channel: str, websocket: WebSocket) -> None:
        async with self.lock:
            if channel in self.connections and websocket in self.connections[channel]:
                self.connections[channel].remove(websocket)
                if not self.connections[channel]:
                    self.connections.pop(channel, None)

    async def broadcast(self, channel: str, message: dict) -> None:
        WS_BROADCAST_COUNTER.labels(channel=channel).inc()
        async with self.lock:
            connections = list(self.connections.get(channel, set()))
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:  # pragma: no cover - safeguard
                await self.unregister(channel, connection)


ws_hub = WebSocketHub()
