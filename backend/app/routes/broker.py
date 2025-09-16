from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..broker.okx import okx_broker
from ..core.responses import success_response

router = APIRouter(prefix="/api/broker/okx", tags=["broker"])


@router.post("/order")
async def post_order(payload: Dict[str, Any], request: Request):
    data = await okx_broker.create_order(payload)
    return success_response(request, data)


@router.post("/order-algo")
async def post_algo_order(payload: Dict[str, Any], request: Request):
    data = await okx_broker.create_algo_order(payload)
    return success_response(request, data)


@router.post("/cancel")
async def post_cancel(payload: Dict[str, Any], request: Request):
    data = await okx_broker.cancel_order(payload)
    return success_response(request, data)


@router.post("/batch-orders")
async def post_batch(payload: Dict[str, Any], request: Request):
    data = await okx_broker.batch_orders(payload)
    return success_response(request, data)


@router.get("/balance")
async def get_balance(request: Request):
    data = await okx_broker.get_balance()
    return success_response(request, data)


@router.get("/open-orders")
async def get_open_orders(instId: str, request: Request):
    data = await okx_broker.get_open_orders(instId)
    return success_response(request, data)


@router.get("/fills-history")
async def get_fills(instId: str, request: Request, start: Optional[str] = None, end: Optional[str] = None):
    data = await okx_broker.get_fills_history(instId, start, end)
    return success_response(request, data)


__all__ = ["router"]
