from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.backtest import run_backtest
from ..main import standard_response

router = APIRouter()


@router.post("/backtest/run")
async def backtest_run(request: Request, payload: Dict[str, Any]):
    strategy = payload.get("strategy", "dca")
    days = int(payload.get("days", 30))
    result = run_backtest(strategy, days)
    return standard_response(request, result)
