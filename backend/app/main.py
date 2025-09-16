from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from .core import env as env_module
from .core.responses import APIError, error_response, success_response
from .core.scheduler import shutdown_scheduler, start_scheduler
from .core.sentry import capture_exception, init_sentry
from .routes import backtest, broker, env, ops, risk, sentiment, strategy, ws

logger = logging.getLogger("ai-trading")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Trading System", default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.2f}ms"
    return response


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    logger.warning("APIError %s: %s", exc.code, exc.message)
    return ORJSONResponse(error_response(request, exc), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    api_error = APIError("BAD_REQUEST", "Validation error", hint=str(exc))
    return ORJSONResponse(error_response(request, api_error), status_code=400)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    capture_exception(exc, route=str(request.url))
    logger.exception("Unhandled exception")
    api_error = APIError("INTERNAL_ERROR", "internal server error")
    return ORJSONResponse(error_response(request, api_error), status_code=500)


@app.on_event("startup")
async def on_startup():
    env_module.ensure_env_file()
    init_sentry()
    start_scheduler()


@app.on_event("shutdown")
async def on_shutdown():
    shutdown_scheduler()


api_router = APIRouter()
api_router.include_router(env.router)
api_router.include_router(broker.router)
api_router.include_router(risk.router)
api_router.include_router(backtest.router)
api_router.include_router(sentiment.router)
api_router.include_router(strategy.router)
api_router.include_router(ops.router)

app.include_router(api_router)
app.include_router(ws.router)


@app.get("/healthz")
async def healthz(request: Request):
    return success_response(request, {"status": "ok"})


@app.get("/")
async def root(request: Request):
    return success_response(request, {"message": "AI trading backend"})
