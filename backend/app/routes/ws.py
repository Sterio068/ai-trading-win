from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.ws_hub import ws_hub

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, channel: str = "orders"):
    await websocket.accept()
    await ws_hub.register(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_hub.unregister(channel, websocket)
