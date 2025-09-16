from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..broker.okx import okx_broker
from ..core.ai import DecisionContext, ai_engine
from ..core.allocator import plan_allocation
from ..core.audit import append_audit
from ..core.backtest import run_backtest
from ..core.env import env_floats, get_env_value
from ..core.responses import APIError, success_response
from ..core.risk import risk_manager
from ..core.scheduler import (
    get_autopilot_state,
    register_strategy_executor,
    set_autopilot_state,
)
from ..core.sentiment import score_texts
from ..core.ws_hub import broadcast

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


class StrategyRequest(BaseModel):
    strategy: Optional[str] = None
    params: Dict[str, Any] = {}
    instId: Optional[str] = None
    sentiment: List[str] = []
    preferred_tier: Optional[str] = None
    mode: Optional[str] = None


class AutopilotStartRequest(BaseModel):
    instId: Optional[str] = None
    base_interval_s: int = 120


async def _execute_strategy(payload: Dict[str, Any], request_id: str, source: str = "manual") -> Dict[str, Any]:
    numbers = env_floats(
        [
            ("TOTAL_CAPITAL_USDT", 10000.0),
            ("DAILY_INVEST_LIMIT_USDT", 500.0),
            ("SINGLE_TRADE_LIMIT_USDT", 50.0),
        ]
    )
    allocation = plan_allocation()
    risk_state = risk_manager.get_state()
    sentiment = score_texts(payload.get("sentiment", []))

    backtest_result = None
    backtest_confidence = 0.5
    if payload.get("strategy"):
        backtest_payload = {
            "strategy": payload.get("strategy"),
            "params": payload.get("params", {}),
        }
        backtest_result = run_backtest(backtest_payload)
        backtest_confidence = max(min(backtest_result["stats"].get("win_rate", 0.5), 1.0), 0.0)

    total_exposure = sum(float(v) for v in risk_state.get("symbol_exposure", {}).values())
    daily_limit = allocation.get("daily_limit", numbers["DAILY_INVEST_LIMIT_USDT"])
    single_limit = allocation.get("single_trade_limit", numbers["SINGLE_TRADE_LIMIT_USDT"])
    if daily_limit <= 0:
        raise APIError("RISK_BUDGET", "Daily invest limit is zero")

    equity = allocation.get("total_capital", numbers["TOTAL_CAPITAL_USDT"]) + float(
        risk_state.get("realized_pnl", 0.0)
    )
    peak = risk_state.get("equity_peak") or equity
    drawdown = max((peak - equity) / peak, 0.0) if peak else 0.0
    capital_remaining_ratio = max(daily_limit - total_exposure, 0.0) / max(daily_limit, 1.0)

    ctx = DecisionContext(
        volatility=float(payload.get("volatility", 1.0)),
        exposure_ratio=total_exposure / max(daily_limit, 1.0),
        drawdown_pct=drawdown,
        backtest_confidence=float(backtest_confidence),
        capital_remaining=capital_remaining_ratio,
        sentiment_score=float(sentiment.get("score", 0.0)),
        allocation=allocation,
        preferred_tier=payload.get("preferred_tier", get_env_value("OPENAI_MODEL_TIER", "gpt-5-nano")),
    )
    decision = await ai_engine.decide(ctx)

    dry_run = source == "ping" or bool(payload.get("dry_run"))

    if dry_run:
        mode = get_env_value("MODE", "paper")
        result = {
            "orders": decision.get("decisions", []),
            "tier": decision.get("tier"),
            "cost": decision.get("cost"),
            "next_interval_s": decision.get("next_interval_s"),
            "sentiment": sentiment,
            "allocation": allocation,
            "mode": mode,
            "dry_run": True,
        }
        if backtest_result:
            result["backtest"] = backtest_result
        append_audit(
            event=f"strategy.execute.{source}",
            route="/api/strategy/execute",
            request_id=request_id,
            request=payload,
            response=result,
            risk_state=risk_manager.get_state(),
            cost_usd=decision.get("cost", 0.0) if decision else 0.0,
            tier=decision.get("tier", "") if decision else "",
        )
        return result

    orders: List[Dict[str, Any]] = []
    total_notional = 0.0
    mode = get_env_value("MODE", "paper")
    allocation_list = allocation.get("allocations", [])

    for idx, suggestion in enumerate(decision.get("decisions", [])):
        inst_id = suggestion.get("instId") or payload.get("instId")
        if not inst_id and allocation_list:
            inst_id = allocation_list[0]["instId"]
        inst_id = inst_id or "BTC-USDT"
        notional = float(suggestion.get("notional", 0.0))
        if notional <= 0:
            continue
        notional = min(notional, single_limit)
        if total_notional + notional > daily_limit:
            raise APIError("RISK_BUDGET", "Daily invest limit reached")
        ok, reason = risk_manager.guard(
            symbol=inst_id,
            notional=notional,
            now=time.time(),
            equity=equity,
        )
        if not ok:
            code, hint = (reason.split(":", 1) + [""])[:2]
            raise APIError(code, "Risk guard blocked", hint=hint or None)
        order_payload = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": suggestion.get("side", "buy"),
            "ordType": suggestion.get("ordType", "market"),
            "notional": str(round(notional, 2)),
            "clOrdId": f"AI-{request_id[:8]}-{idx}",
        }
        if order_payload["ordType"] == "limit" and suggestion.get("px"):
            order_payload["px"] = str(round(float(suggestion.get("px", 0)), 6))
        response = await okx_broker.create_order(order_payload)
        total_notional += notional
        risk_manager.on_order_commit(symbol=inst_id, notional=notional, now=time.time())
        if suggestion.get("sl_tp"):
            base_px = float(suggestion.get("px") or 1.0)
            sl = base_px * (1 - suggestion["sl_tp"].get("sl_pct", 0.01))
            tp = base_px * (1 + suggestion["sl_tp"].get("tp_pct", 0.02))
            algo_payload = {
                "instId": inst_id,
                "side": suggestion.get("side", "buy"),
                "ordType": "oco",
                "tpTriggerPx": f"{tp:.4f}",
                "slTriggerPx": f"{sl:.4f}",
                "sz": "1",
            }
            await okx_broker.create_algo_order(algo_payload)
        orders.append({"request": order_payload, "response": response})

    result = {
        "orders": orders,
        "tier": decision.get("tier"),
        "cost": decision.get("cost"),
        "next_interval_s": decision.get("next_interval_s"),
        "sentiment": sentiment,
        "allocation": allocation,
        "mode": mode,
    }
    if backtest_result:
        result["backtest"] = backtest_result

    await broadcast("orders/fills", {"orders": orders})
    await broadcast("risk", risk_manager.get_state())

    append_audit(
        event=f"strategy.execute.{source}",
        route="/api/strategy/execute",
        request_id=request_id,
        request=payload,
        response=result,
        risk_state=risk_manager.get_state(),
        cost_usd=decision.get("cost", 0.0) if decision else 0.0,
        tier=decision.get("tier", "") if decision else "",
    )
    return result


@router.post("/execute")
async def execute_strategy(payload: StrategyRequest, request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    result = await _execute_strategy(payload.model_dump(), request_id, source=payload.mode or "manual")
    return success_response(request, result)


@router.post("/autopilot/start")
async def autopilot_start(payload: AutopilotStartRequest, request: Request):
    state = set_autopilot_state(True, max(payload.base_interval_s, 30), payload.instId)
    await broadcast("autopilot", state)
    return success_response(request, state)


@router.post("/autopilot/stop")
async def autopilot_stop(request: Request):
    state = set_autopilot_state(False, get_autopilot_state().get("base_interval_s", 120))
    await broadcast("autopilot", state)
    return success_response(request, state)


def _autopilot_executor_factory():
    async def _executor(payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        try:
            result = await _execute_strategy(payload, request_id, source="autopilot")
            return result
        except APIError as exc:
            append_audit(
                event="strategy.execute.autopilot.error",
                route="/api/strategy/execute",
                request_id=request_id,
                request=payload,
                response={"error": exc.code},
                code=exc.code,
                message=exc.message,
            )
            return {
                "error": {"code": exc.code, "message": exc.message},
                "next_interval_s": get_autopilot_state().get("base_interval_s", 120),
            }

    return _executor


register_strategy_executor(_autopilot_executor_factory())


__all__ = ["router"]
