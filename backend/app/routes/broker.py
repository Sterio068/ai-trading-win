from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..broker.okx import okx_broker
from ..core.ws_hub import ws_hub
from ..main import standard_response

router = APIRouter()


@router.get("/broker/okx/balance")
async def okx_balance(request: Request):
    balance = await okx_broker.get_balance()
    return standard_response(request, balance)


@router.post("/broker/okx/order")
async def okx_order(request: Request, payload: Dict[str, Any]):
    response = await okx_broker.place_order(payload)
    await ws_hub.broadcast("orders", {"type": "order", "payload": response})
    return standard_response(request, response)


@router.post("/broker/okx/simulate")
async def okx_simulate(request: Request, payload: Dict[str, Any]):
    response = await okx_broker.simulate_order(payload)
    await ws_hub.broadcast("orders", {"type": "simulate", "payload": response})
    return standard_response(request, response)
