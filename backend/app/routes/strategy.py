from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.ai import ai_engine
from ..core.scheduler import autopilot_controller
from ..core.ws_hub import ws_hub
from ..main import standard_response

router = APIRouter()

STRATEGIES = [
    {"name": "dca", "description": "Dollar-cost averaging", "complexity": 1},
    {"name": "breakout", "description": "Momentum breakout", "complexity": 2},
    {"name": "grid", "description": "Grid trading", "complexity": 3},
]


@router.get("/strategy/list")
async def strategy_list(request: Request):
    return standard_response(request, STRATEGIES)


@router.post("/strategy/execute")
async def strategy_execute(request: Request, payload: Dict[str, Any]):
    strategy = payload.get("strategy", "dca")
    context = {"universe": payload.get("universe", ai_engine.universe)}
    decision = await ai_engine.decide(strategy, context)
    await ws_hub.broadcast("orders", {"type": "strategy", "payload": decision})
    return standard_response(request, decision)


@router.post("/strategy/autopilot/start")
async def autopilot_start(request: Request, payload: Dict[str, Any] | None = None):
    interval = (payload or {}).get("interval")
    state = await autopilot_controller.start(interval)
    await ws_hub.broadcast("autopilot", {"type": "start", "payload": state})
    return standard_response(request, state)


@router.post("/strategy/autopilot/stop")
async def autopilot_stop(request: Request):
    state = await autopilot_controller.stop()
    await ws_hub.broadcast("autopilot", {"type": "stop", "payload": state})
    return standard_response(request, state)


@router.get("/strategy/autopilot/status")
async def autopilot_status(request: Request):
    return standard_response(request, autopilot_controller.status())
