from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.ws_hub import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)


__all__ = ["router"]
