from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List

from .cost import evaluate_tier, register_cost
from .env import get_env_value
from .responses import APIError


@dataclass
class DecisionContext:
    volatility: float
    exposure_ratio: float
    drawdown_pct: float
    backtest_confidence: float
    capital_remaining: float
    sentiment_score: float
    allocation: Dict[str, Any]
    preferred_tier: str


class AIEngine:
    def __init__(self) -> None:
        self._last_interval = 120.0

    def _compute_complexity(self, ctx: DecisionContext) -> float:
        vol_factor = min(max(ctx.volatility, 0.1), 3.0)
        exposure_factor = 1.0 + ctx.exposure_ratio
        dd_factor = 1.0 + max(ctx.drawdown_pct, 0.0)
        confidence_penalty = max(1.0 - ctx.backtest_confidence, 0.3)
        sentiment = 1.0 + abs(ctx.sentiment_score)
        return vol_factor * exposure_factor * dd_factor * confidence_penalty * sentiment

    def _frequency_multiplier(self, ctx: DecisionContext, remaining_budget: float) -> float:
        base = 1.0
        if ctx.volatility > 1.0:
            base *= 0.7
        if ctx.sentiment_score < -0.4:
            base *= 1.3
        if remaining_budget < 0.3:
            base *= 1.8
        return max(0.3, min(base, 2.5))

    def _generate_decisions(self, ctx: DecisionContext) -> List[Dict[str, Any]]:
        allocations = ctx.allocation.get("allocations", [])
        if not allocations:
            return []
        decisions = []
        bias = "buy" if ctx.sentiment_score >= 0 else "sell"
        for item in allocations:
            weight = item.get("weight", 0.0)
            notional = min(item.get("notional", 0.0), ctx.allocation.get("single_trade_limit", 0.0))
            if notional <= 0:
                continue
            ord_type = "market" if ctx.volatility < 1.5 else "limit"
            price_offset = 1.0 + random.uniform(-0.002, 0.002)
            decisions.append(
                {
                    "instId": item["instId"],
                    "side": bias,
                    "ordType": ord_type,
                    "notional": round(notional, 2),
                    "px": price_offset,
                    "sl_tp": {
                        "sl_pct": 0.01 + 0.01 * (1 - ctx.backtest_confidence),
                        "tp_pct": 0.02 + 0.02 * ctx.backtest_confidence,
                    },
                }
            )
        return decisions

    async def decide(self, ctx: DecisionContext) -> Dict[str, Any]:
        preferred = ctx.preferred_tier or get_env_value("OPENAI_MODEL_TIER", "gpt-5-nano")
        tier, cost, allowed, reason = evaluate_tier(preferred)
        if not allowed:
            raise APIError("AI_BUDGET", "AI budget exhausted", hint=reason)

        complexity = self._compute_complexity(ctx)
        remaining_ratio = ctx.capital_remaining
        freq_multiplier = self._frequency_multiplier(ctx, remaining_ratio)
        next_interval = max(30.0, self._last_interval * freq_multiplier)
        decisions = self._generate_decisions(ctx)
        register_cost(tier, cost)
        self._last_interval = next_interval
        return {
            "tier": tier,
            "reason": reason or "ok",
            "cost": cost,
            "complexity": complexity,
            "next_interval_s": next_interval,
            "decisions": decisions,
        }


ai_engine = AIEngine()


__all__ = ["AIEngine", "DecisionContext", "ai_engine"]
