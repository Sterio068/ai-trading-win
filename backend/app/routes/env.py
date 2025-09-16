from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..core.audit import append_audit
from ..core.env import mask_value, masked_env, switch_mode, update_env
from ..core.responses import APIError, success_response
from ..core.ws_hub import broadcast

router = APIRouter(prefix="/api/env", tags=["env"])


class EnvUpdateRequest(BaseModel):
    values: Dict[str, str]
    updated_by: str | None = None


class SwitchModeRequest(BaseModel):
    mode: str


@router.get("")
async def get_env(request: Request):
    data = {"values": masked_env()}
    return success_response(request, data)


@router.post("")
async def update_env_values(payload: EnvUpdateRequest, request: Request):
    result = update_env(payload.values)
    diff_masked = {
        key: {
            "old": mask_value(old),
            "new": mask_value(new),
        }
        for key, (old, new) in result.diff.items()
    }
    response = {"diff": diff_masked}
    await broadcast("settings:update", response)
    append_audit(
        event="env.update",
        route="/api/env",
        request_id=getattr(request.state, "request_id", ""),
        user=payload.updated_by or "system",
        request=payload.model_dump(),
        response=response,
    )
    return success_response(request, response)


@router.post("/switch-mode")
async def switch_env_mode(payload: SwitchModeRequest, request: Request):
    try:
        result = switch_mode(payload.mode)
    except ValueError as exc:
        raise APIError("BAD_REQUEST", str(exc)) from exc
    diff_masked = {
        key: {
            "old": mask_value(old),
            "new": mask_value(new),
        }
        for key, (old, new) in result.diff.items()
    }
    await broadcast("settings:update", {"diff": diff_masked})
    append_audit(
        event="env.switch_mode",
        route="/api/env/switch-mode",
        request_id=getattr(request.state, "request_id", ""),
        request=payload.model_dump(),
        response={"diff": diff_masked},
    )
    return success_response(request, {"diff": diff_masked})


__all__ = ["router"]
