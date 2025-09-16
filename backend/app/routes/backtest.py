from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.audit import append_audit
from ..core.backtest import run_backtest
from ..core.responses import success_response

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
async def run_backtest_route(payload: Dict[str, Any], request: Request):
    result = run_backtest(payload)
    append_audit(
        event="backtest.run",
        route="/api/backtest/run",
        request_id=getattr(request.state, "request_id", ""),
        request=payload,
        response=result,
    )
    return success_response(request, result)


__all__ = ["router"]
