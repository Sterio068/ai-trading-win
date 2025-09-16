from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from .env import env_manager
from .metrics import AI_GUARD_COUNTER, record_cost_remaining


class CostManager:
    def __init__(self) -> None:
        self.spent = 0.0
        self.last_reset = datetime.now(timezone.utc).date()
        self.update_limit()

    def update_limit(self) -> None:
        limit = env_manager.get("AI_DAILY_COST_LIMIT_USD", "0") or "0"
        try:
            self.limit = float(limit)
        except ValueError:
            self.limit = 0.0
        record_cost_remaining(max(self.limit - self.spent, 0.0))

    def _ensure_reset(self) -> None:
        today = datetime.now(timezone.utc).date()
        if today != self.last_reset:
            self.spent = 0.0
            self.last_reset = today
            record_cost_remaining(self.limit)

    def can_spend(self, cost: float) -> bool:
        self._ensure_reset()
        return (self.spent + cost) <= self.limit if self.limit else True

    def record(self, cost: float) -> None:
        self._ensure_reset()
        self.spent += cost
        record_cost_remaining(max(self.limit - self.spent, 0.0))

    def budget(self) -> Dict[str, float]:
        self._ensure_reset()
        return {"limit": self.limit, "spent": self.spent, "remaining": max(self.limit - self.spent, 0.0)}

    def guard(self, cost: float) -> bool:
        if self.can_spend(cost):
            AI_GUARD_COUNTER.labels(action="allow").inc()
            return True
        AI_GUARD_COUNTER.labels(action="block").inc()
        return False


cost_manager = CostManager()
