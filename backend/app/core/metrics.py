from __future__ import annotations

from typing import Any, Dict

from fastapi import Response
from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

REQUEST_COUNTER = Counter("app_requests_total", "Number of HTTP requests", ["route"])
AI_MODEL_COUNTER = Counter("ai_model_invocations_total", "AI model usage", ["model", "decision"])
AI_GUARD_COUNTER = Counter("ai_cost_guard_total", "AI cost guard actions", ["action"])
ORDER_COUNTER = Counter("orders_total", "Number of broker orders", ["side", "type"])
SCHEDULER_TICK_COUNTER = Counter("scheduler_ticks_total", "Scheduler ticks", ["job"])
WS_BROADCAST_COUNTER = Counter("ws_broadcast_total", "Websocket broadcasts", ["channel"])
COST_REMAINING_GAUGE = Gauge("ai_cost_remaining", "Remaining AI cost", ["currency"])

EXECUTION_DURATION = Histogram(
    "ai_execution_seconds",
    "AI decision execution time",
    buckets=(0.01, 0.1, 0.5, 1, 2, 5, 10),
)


def metrics_response() -> Response:
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)


def record_cost_remaining(amount: float) -> None:
    COST_REMAINING_GAUGE.labels(currency="USD").set(amount)
