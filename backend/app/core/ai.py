from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .allocator import allocator
from .cost import cost_manager
from .env import env_manager
from .metrics import AI_MODEL_COUNTER, EXECUTION_DURATION, ORDER_COUNTER
from .risk import risk_manager

MODEL_ORDER = ["GPT-5", "GPT-5-MINI", "gpt-5-nano"]


@dataclass
class ModelTier:
    name: str
    cost: float


MODEL_TIERS: Dict[str, ModelTier] = {
    "GPT-5": ModelTier("GPT-5", 0.12),
    "GPT-5-MINI": ModelTier("GPT-5-MINI", 0.06),
    "gpt-5-nano": ModelTier("gpt-5-nano", 0.02),
}


class AIEngine:
    def __init__(self) -> None:
        self.universe = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT"]

    def _preferred_models(self) -> List[str]:
        base = env_manager.get("OPENAI_MODEL_TIER", "GPT-5-MINI")
        if base not in MODEL_ORDER:
            base = "GPT-5-MINI"
        idx = MODEL_ORDER.index(base)
        return MODEL_ORDER[: idx + 1]

    def select_model(self, complexity: int) -> Optional[ModelTier]:
        candidates = self._preferred_models()
        if complexity <= 1 and "gpt-5-nano" in candidates:
            candidates = ["gpt-5-nano"] + [c for c in candidates if c != "gpt-5-nano"]
        remaining = cost_manager.budget().get("remaining", 0.0)
        for name in candidates:
            tier = MODEL_TIERS[name]
            if remaining < tier.cost * 0.5:
                continue
            if cost_manager.guard(tier.cost):
                return tier
        cheapest = MODEL_TIERS["gpt-5-nano"]
        if cost_manager.guard(cheapest.cost):
            return cheapest
        return None

    def estimate_complexity(self, strategy: str, context: Dict[str, Any]) -> int:
        size = len(context.get("universe", []))
        if strategy.lower() == "grid" or size > 3:
            return 3
        if strategy.lower() == "breakout" or size > 2:
            return 2
        return 1

    async def decide(self, strategy: str, context: Dict[str, Any]) -> Dict[str, Any]:
        complexity = self.estimate_complexity(strategy, context)
        with EXECUTION_DURATION.time():
            tier = self.select_model(complexity)
            if not tier:
                return {
                    "model": None,
                    "status": "skipped",
                    "reason": "budget_exhausted",
                    "daily_cost": cost_manager.budget(),
                }
            AI_MODEL_COUNTER.labels(model=tier.name, decision=strategy).inc()
            cost_manager.record(tier.cost)
            total_capital = float(env_manager.get("TOTAL_CAPITAL_USDT", "0") or 0)
            allocations = allocator.allocate(context.get("universe", self.universe[:2]), total_capital)
            orders = []
            from ..broker.okx import okx_broker  # local import

            for allocation in allocations:
                symbol = allocation["symbol"]
                size = allocation["allocation"]
                risk = risk_manager.evaluate_order(symbol, size)
                if not risk["allowed"]:
                    orders.append({
                        "symbol": symbol,
                        "size": size,
                        "status": "blocked",
                        "reasons": risk["reasons"],
                    })
                    continue
                order_payload = {
                    "instId": symbol,
                    "tdMode": "cash",
                    "side": "buy",
                    "ordType": "market",
                    "sz": round(size / 1000, 4),
                }
                ORDER_COUNTER.labels(side="buy", type="market").inc()
                okx_response = await okx_broker.simulate_order(order_payload)
                risk_manager.register_fill(symbol, pnl=0.0, size_usd=size)
                orders.append({
                    "symbol": symbol,
                    "size": size,
                    "status": "submitted",
                    "broker_response": okx_response,
                })
            return {
                "model": tier.name,
                "strategy": strategy,
                "orders": orders,
                "daily_cost": cost_manager.budget(),
                "universe": context.get("universe", self.universe),
            }

    async def execute_autopilot(self) -> Dict[str, Any]:
        strategy = "autopilot"
        context = {"universe": self.universe}
        decision = await self.decide(strategy, context)
        decision["decision"] = strategy
        return decision


aI_engine_singleton = AIEngine()
ai_engine = aI_engine_singleton
