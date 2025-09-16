from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

AUDIT_PATH = Path(__file__).resolve().parents[2] / "exports" / "audit_log.csv"
AUDIT_FIELDS = [
    "ts",
    "event",
    "route",
    "request_id",
    "user",
    "request_json",
    "response_json",
    "risk_state",
    "code",
    "message",
    "cost_usd",
    "tier",
]


def ensure_file() -> None:
    if not AUDIT_PATH.exists():
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=AUDIT_FIELDS)
            writer.writeheader()


def append_audit(
    *,
    event: str,
    route: str,
    request_id: str,
    user: str = "system",
    request: Optional[Dict[str, Any]] = None,
    response: Optional[Dict[str, Any]] = None,
    risk_state: Optional[Dict[str, Any]] = None,
    code: str = "",
    message: str = "",
    cost_usd: float = 0.0,
    tier: str = "",
) -> None:
    ensure_file()
    row = {
        "ts": datetime.utcnow().isoformat(),
        "event": event,
        "route": route,
        "request_id": request_id,
        "user": user,
        "request_json": json.dumps(request or {}, ensure_ascii=False),
        "response_json": json.dumps(response or {}, ensure_ascii=False),
        "risk_state": json.dumps(risk_state or {}, ensure_ascii=False),
        "code": code,
        "message": message,
        "cost_usd": f"{cost_usd:.6f}",
        "tier": tier,
    }
    with AUDIT_PATH.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=AUDIT_FIELDS)
        writer.writerow(row)


__all__ = ["append_audit"]
