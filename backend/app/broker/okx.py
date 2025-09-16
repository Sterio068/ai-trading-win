from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

import httpx

from ..core.env import env_manager
from ..core.metrics import ORDER_COUNTER
from .base import BaseBroker

API_BASE = "https://www.okx.com"


class OkxBroker(BaseBroker):
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=API_BASE, timeout=10.0)

    async def close(self) -> None:
        await self.client.aclose()

    def _credentials(self) -> Dict[str, str]:
        mode = env_manager.mode
        suffix = "PAPER" if mode == "PAPER" else "REAL"
        return {
            "api_key": env_manager.get(f"OKX_API_KEY_{suffix}"),
            "secret": env_manager.get(f"OKX_API_SECRET_{suffix}"),
            "passphrase": env_manager.get(f"OKX_API_PASSPHRASE_{suffix}"),
        }

    def _sign(self, timestamp: str, method: str, path: str, body: str, secret: str) -> str:
        message = f"{timestamp}{method}{path}{body}"
        mac = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def _headers(self, method: str, path: str, body: str) -> Dict[str, str]:
        creds = self._credentials()
        timestamp = str(time.time())
        if not creds["api_key"]:
            return {}
        sign = self._sign(timestamp, method, path, body, creds["secret"])
        headers = {
            "OK-ACCESS-KEY": creds["api_key"],
            "OK-ACCESS-PASSPHRASE": creds["passphrase"],
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-SIGN": sign,
            "Content-Type": "application/json",
        }
        if env_manager.mode == "PAPER":
            headers["x-simulated-trading"] = "1"
        return headers

    async def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        body = json.dumps(payload or {}) if payload else ""
        headers = self._headers(method, path, body)
        if not headers:
            # return simulated response when no credentials
            return {"code": "0", "data": payload or {}, "simulated": True}
        response = await self.client.request(method, path, content=body, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_balance(self) -> Dict[str, Any]:
        try:
            resp = await self._request("GET", "/api/v5/account/balance")
        except Exception:
            resp = {
                "code": "0",
                "data": [{"ccy": "USDT", "availBal": "1000", "cashBal": "1000"}],
                "simulated": True,
            }
        return resp

    async def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ORDER_COUNTER.labels(side=payload.get("side", "unknown"), type=payload.get("ordType", "unknown")).inc()
        try:
            resp = await self._request("POST", "/api/v5/trade/order", payload)
        except Exception:
            resp = {"code": "0", "data": [payload], "simulated": True}
        return resp

    async def simulate_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"code": "0", "data": [payload], "simulated": True, "ts": time.time()}


okx_broker = OkxBroker()
