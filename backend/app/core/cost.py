from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict

from .env import get_env_value
from .metrics import ai_budget_left_usd, ai_calls_total, ai_cost_usd_total

COST_PATH = Path(__file__).resolve().parents[2] / "storage" / "ai_cost.json"
COST_TABLE = {
    "gpt-5": 0.02,
    "gpt-5-mini": 0.005,
    "gpt-5-nano": 0.001,
}


def _load_state() -> Dict[str, Any]:
    if not COST_PATH.exists():
        return {"date": date.today().isoformat(), "totals": {}, "count": {}}
    with COST_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_state(state: Dict[str, Any]) -> None:
    COST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def _ensure_today(state: Dict[str, Any]) -> Dict[str, Any]:
    today = date.today().isoformat()
    if state.get("date") != today:
        state = {"date": today, "totals": {}, "count": {}}
    return state


def _daily_limit() -> float:
    try:
        return float(get_env_value("AI_DAILY_COST_LIMIT_USD", "3.0"))
    except ValueError:
        return 3.0


def evaluate_tier(requested: str) -> Tuple[str, float, bool, str]:
    state = _ensure_today(_load_state())
    limit = _daily_limit()
    spent = sum(state.get("totals", {}).values())
    remaining = max(limit - spent, 0.0)
    ai_budget_left_usd.set(remaining)
    if remaining <= 0:
        return requested, 0.0, False, "budget exhausted"

    tiers = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    if requested not in tiers:
        requested = "gpt-5-nano"
    requested_index = tiers.index(requested)

    # Force downgrade when budget < 10%
    if limit > 0 and remaining / limit <= 0.1:
        forced_cost = COST_TABLE["gpt-5-nano"]
        if remaining < forced_cost:
            return "gpt-5-nano", forced_cost, False, "budget exhausted"
        if requested != "gpt-5-nano":
            return "gpt-5-nano", forced_cost, True, "budget low, forced downgrade"

    for idx in range(requested_index, len(tiers)):
        tier = tiers[idx]
        cost = COST_TABLE[tier]
        if remaining >= cost:
            return tier, cost, True, ""
    return requested, COST_TABLE["gpt-5-nano"], False, "budget exhausted"


def register_cost(tier: str, cost: float) -> None:
    state = _ensure_today(_load_state())
    totals = state.setdefault("totals", {})
    counts = state.setdefault("count", {})
    totals[tier] = float(totals.get(tier, 0.0)) + cost
    counts[tier] = int(counts.get(tier, 0)) + 1
    _save_state(state)
    ai_budget_left_usd.set(max(_daily_limit() - sum(totals.values()), 0.0))
    ai_calls_total.labels(tier=tier).inc()
    ai_cost_usd_total.labels(tier=tier).inc(cost)


def get_cost_snapshot() -> Dict[str, Any]:
    state = _ensure_today(_load_state())
    limit = _daily_limit()
    spent = {tier: float(value) for tier, value in state.get("totals", {}).items()}
    remaining = max(limit - sum(spent.values()), 0.0)
    ai_budget_left_usd.set(remaining)
    return {
        "date": state.get("date"),
        "totals": spent,
        "count": state.get("count", {}),
        "limit": limit,
        "remaining": remaining,
    }


__all__ = ["evaluate_tier", "register_cost", "get_cost_snapshot"]
