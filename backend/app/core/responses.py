from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from fastapi import Request, status


class APIError(Exception):
    """Domain specific exception with structured error codes."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        hint: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.status_code = status_code
        self.payload = payload or {}


ERROR_CODES = {
    "BAD_REQUEST",
    "UNAUTHORIZED",
    "EXCHANGE_REJECT",
    "EXCHANGE_TIME_SKEW",
    "RISK_DAILY_CAP",
    "RISK_EXPOSURE_LIMIT",
    "RISK_COOLDOWN",
    "RISK_DD_STOP",
    "RISK_BUDGET",
    "AI_BUDGET",
    "NOT_FOUND",
    "CONFLICT",
    "INTERNAL_ERROR",
}


def _ensure_error_code(code: str) -> str:
    if code not in ERROR_CODES:
        return "INTERNAL_ERROR"
    return code


def success_response(request: Request, data: Any) -> Dict[str, Any]:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return {
        "ok": True,
        "data": data,
        "meta": {
            "request_id": request_id,
            "ts": int(time.time() * 1000),
        },
    }


def error_response(request: Request, error: APIError) -> Dict[str, Any]:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return {
        "ok": False,
        "error": {
            "code": _ensure_error_code(error.code),
            "message": error.message,
            "hint": error.hint,
            **error.payload,
        },
        "meta": {
            "request_id": request_id,
            "ts": int(time.time() * 1000),
        },
    }


__all__ = ["APIError", "success_response", "error_response"]
