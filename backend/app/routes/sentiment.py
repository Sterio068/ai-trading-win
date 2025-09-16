from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from ..core.sentiment import aggregate_sentiment
from ..main import standard_response

router = APIRouter()


@router.post("/sentiment/aggregate")
async def sentiment_aggregate(request: Request, payload: Dict[str, Any]):
    text = payload.get("text", "")
    result = aggregate_sentiment(text)
    return standard_response(request, result)
