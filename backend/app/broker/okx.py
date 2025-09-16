from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from ..core.env import read_env
from .base import Broker
from ..core.metrics import order_submit_reject, order_submit_success, order_submit_total
from ..core.responses import APIError
from ..core.sentry import capture_message

BASE_URL = "https://www.okx.com"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _sign(secret: str, message: str) -> str:
    signature = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


class OKXBroker(Broker):
    def __init__(self) -> None:
        self.base_url = BASE_URL

    def _credentials(self) -> Dict[str, str]:
        env = read_env()
        mode = env.get("MODE", "paper")
        if mode == "real":
            return {
                "api_key": env.get("OKX_API_KEY_REAL", ""),
                "api_secret": env.get("OKX_API_SECRET_REAL", ""),
                "passphrase": env.get("OKX_PASSPHRASE_REAL", ""),
                "mode": mode,
            }
        return {
            "api_key": env.get("OKX_API_KEY_PAPER", ""),
            "api_secret": env.get("OKX_API_SECRET_PAPER", ""),
            "passphrase": env.get("OKX_PASSPHRASE_PAPER", ""),
            "mode": "paper",
        }

    async def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        creds = self._credentials()
        mode = creds["mode"]
        timestamp = _timestamp()
        body = json.dumps(payload or {}) if payload else ""
        message = f"{timestamp}{method.upper()}{path}{body}"
        headers = {
            "OK-ACCESS-KEY": creds["api_key"],
            "OK-ACCESS-PASSPHRASE": creds["passphrase"],
            "OK-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        }
        if mode == "paper":
            headers["x-simulated-trading"] = "1"
        if creds["api_secret"]:
            headers["OK-ACCESS-SIGN"] = _sign(creds["api_secret"], message)
        else:
            # simulate if missing secrets
            return self._simulate_response(method, path, payload, params)

        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(method, url, json=payload, params=params, headers=headers)
            data = response.json()
        except httpx.RequestError:
            capture_message(
                "okx_request_error",
                exchange="okx",
                mode=mode,
                route=path,
            )
            return self._simulate_response(method, path, payload, params)

        if data.get("code") not in ("0", 0, None):
            code = data.get("code", "-1")
            order_submit_reject.labels(exchange="okx", mode=mode, code=code).inc()
            raise APIError("EXCHANGE_REJECT", data.get("msg", "exchange error"))
        return data

    def _simulate_response(self, method: str, path: str, payload: Optional[Dict[str, Any]], params: Optional[Dict[str, str]]) -> Dict[str, Any]:
        if path.endswith("balance"):
            return {
                "code": "0",
                "data": [
                    {
                        "totalEq": "10000",
                        "details": [
                            {"ccy": "USDT", "cashBal": "5000", "availBal": "4800"},
                            {"ccy": "BTC", "cashBal": "0.5", "availBal": "0.45"},
                        ],
                    }
                ],
            }
        if path.endswith("orders-pending"):
            return {"code": "0", "data": []}
        if path.endswith("fills-history"):
            return {"code": "0", "data": []}
        # Orders simulation
        order_id = f"SIM-{datetime.utcnow().strftime('%H%M%S%f')}"
        return {
            "code": "0",
            "data": [
                {
                    "ordId": order_id,
                    "clOrdId": payload.get("clOrdId") if payload else order_id,
                    "state": "filled" if payload and payload.get("ordType") == "market" else "live",
                }
            ],
        }

    async def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        order_submit_total.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        data = await self._request("POST", "/api/v5/trade/order", payload)
        order_submit_success.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        return data

    async def create_algo_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        order_submit_total.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        data = await self._request("POST", "/api/v5/trade/order-algo", payload)
        order_submit_success.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        return data

    async def cancel_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/api/v5/trade/cancel-order", payload)

    async def batch_orders(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        order_submit_total.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        data = await self._request("POST", "/api/v5/trade/batch-orders", payload)
        order_submit_success.labels(exchange="okx", mode=self._credentials()["mode"]).inc()
        return data

    async def get_balance(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v5/account/balance")

    async def get_open_orders(self, inst_id: str) -> Dict[str, Any]:
        params = {"instId": inst_id}
        return await self._request("GET", "/api/v5/trade/orders-pending", params=params)

    async def get_fills_history(self, inst_id: str, start: Optional[str], end: Optional[str]) -> Dict[str, Any]:
        params = {"instId": inst_id}
        if start:
            params["after"] = start
        if end:
            params["before"] = end
        return await self._request("GET", "/api/v5/trade/fills-history", params=params)


okx_broker = OKXBroker()


__all__ = ["okx_broker", "OKXBroker"]
