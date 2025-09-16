from __future__ import annotations

from fastapi import APIRouter, Request

from ..core.cost import cost_manager
from ..core.metrics import metrics_response
from ..main import standard_response

router = APIRouter()


@router.get("/ops/metrics")
async def ops_metrics():
    return metrics_response()


@router.get("/ops/cost")
async def ops_cost(request: Request):
    return standard_response(request, cost_manager.budget())
