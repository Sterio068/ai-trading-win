from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.cost import cost_manager
from ..core.env import env_manager
from ..core.ws_hub import ws_hub
from ..main import standard_response

router = APIRouter()


@router.get("/env")
async def get_env(request: Request):
    return standard_response(request, env_manager.masked_env())


@router.post("/env")
async def update_env(request: Request, payload: Dict[str, Any]):
    env_manager.update_env(payload)
    cost_manager.update_limit()
    await ws_hub.broadcast("settings:update", {"type": "env", "payload": env_manager.masked_env()})
    return standard_response(request, env_manager.masked_env())


@router.post("/env/switch-mode")
async def switch_mode(request: Request, payload: Dict[str, Any]):
    mode = payload.get("mode", "PAPER")
    try:
        env_manager.switch_mode(mode)
    except ValueError as exc:
        return standard_response(
            request,
            ok=False,
            error={"code": "invalid_mode", "message": str(exc), "hint": "Use PAPER or REAL"},
            data=None,
            status_code=400,
        )
    await ws_hub.broadcast("settings:update", {"type": "mode", "payload": env_manager.mode})
    return standard_response(request, {"mode": env_manager.mode})
