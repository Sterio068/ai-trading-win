from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..core.audit import append_audit
from ..core.responses import success_response
from ..core.risk import risk_manager

router = APIRouter(prefix="/api/risk", tags=["risk"])


class RiskConfigUpdate(BaseModel):
    config: Dict[str, Any]
    updated_by: str | None = None


@router.get("/version")
async def get_risk_version(request: Request):
    data = risk_manager.get_version_info()
    return success_response(request, data)


@router.get("/config")
async def get_risk_config(request: Request):
    return success_response(request, risk_manager.config)


@router.post("/config")
async def update_risk_config(payload: RiskConfigUpdate, request: Request):
    result = risk_manager.update_config(payload.config, payload.updated_by or "system")
    append_audit(
        event="risk.config.update",
        route="/api/risk/config",
        request_id=getattr(request.state, "request_id", ""),
        user=payload.updated_by or "system",
        request=payload.model_dump(),
        response=result,
    )
    return success_response(request, result)


@router.get("/state")
async def get_risk_state(request: Request):
    return success_response(request, risk_manager.get_state())


__all__ = ["router"]
