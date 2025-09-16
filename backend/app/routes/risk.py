from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.risk import risk_manager
from ..main import standard_response

router = APIRouter()


@router.get("/risk/status")
async def risk_status(request: Request):
    return standard_response(request, risk_manager.status())


@router.post("/risk/config")
async def risk_update(request: Request, payload: Dict[str, Any]):
    risk_manager.update_config(payload)
    return standard_response(request, risk_manager.status())


@router.post("/risk/reset")
async def risk_reset(request: Request):
    risk_manager.reset_day()
    return standard_response(request, risk_manager.status())
