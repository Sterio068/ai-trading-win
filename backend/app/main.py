from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .core.env import env_manager
from .core.metrics import REQUEST_COUNTER
from .core.scheduler import autopilot_controller
from .core.sentry import init_sentry
from .routes import backtest, broker, env, ops, risk, sentiment, strategy, ws

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    init_sentry(env_manager.get("SENTRY_DSN"))

    app = FastAPI(title="AI Quant Trading", version="1.0.0")

    raw_origins = env_manager.get("CORS_ALLOW_ORIGINS", "")
    allow_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()] or [
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next: Callable):
        request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            REQUEST_COUNTER.labels(route=request.url.path).inc()
            logger.debug("Request %s finished in %.4fs", request_id, duration)

    app.include_router(env.router, prefix="/api")
    app.include_router(broker.router, prefix="/api")
    app.include_router(risk.router, prefix="/api")
    app.include_router(backtest.router, prefix="/api")
    app.include_router(sentiment.router, prefix="/api")
    app.include_router(strategy.router, prefix="/api")
    app.include_router(ops.router)
    app.include_router(ws.router)

    @app.get("/healthz", response_class=ORJSONResponse)
    async def healthz(request: Request) -> Dict[str, Any]:
        return standard_response(request, {"status": "ok", "mode": env_manager.mode})

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting application in %s mode", env_manager.mode)
        await autopilot_controller.initialize()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await autopilot_controller.shutdown()

    return app


def standard_response(
    request: Request,
    data: Optional[Any] = None,
    ok: bool = True,
    error: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> ORJSONResponse:
    payload: Dict[str, Any] = {
        "ok": ok,
        "data": data,
        "request_id": getattr(request.state, "request_id", uuid.uuid4().hex),
        "meta": {"ts": datetime.now(timezone.utc).isoformat()},
    }
    if not ok:
        payload["error"] = error or {"code": "unknown", "message": "Unknown error"}
    return ORJSONResponse(status_code=status_code, content=payload)


app = create_app()
