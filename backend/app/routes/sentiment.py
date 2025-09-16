from __future__ import annotations

from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..core.responses import success_response
from ..core.sentiment import score_texts

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])


class SentimentPayload(BaseModel):
    texts: List[str]


@router.post("/aggregate")
async def aggregate_sentiment(payload: SentimentPayload, request: Request):
    result = score_texts(payload.texts)
    return success_response(request, result)


__all__ = ["router"]
