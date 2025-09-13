from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Awaitable
import time
import logging

logger = logging.getLogger("app.mw")

def install_middlewares(app):
    @app.middleware("http")
    async def timing_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        t0 = time.perf_counter()
        try:
            resp = await call_next(request)
            return resp
        finally:
            dt = (time.perf_counter() - t0) * 1000
            logger.debug(f"[HTTP] {request.method} {request.url.path} {dt:.1f}ms")
