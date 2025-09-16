from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from .env import env_manager


@dataclass
class RiskConfig:
    cooldown_seconds: int = 30
    max_exposure_pct: float = 0.3
    daily_loss_limit: float = 1000.0
    max_drawdown_pct: float = 0.2


class RiskManager:
    def __init__(self, config: Optional[RiskConfig] = None) -> None:
        self.config = config or RiskConfig()
        self.last_trade_at: Optional[datetime] = None
        self.daily_loss: float = 0.0
        self.max_equity: float = float(env_manager.get("TOTAL_CAPITAL_USDT", "20000") or 20000)
        self.current_equity: float = self.max_equity
        self.exposure: Dict[str, float] = {}

    def reset_day(self) -> None:
        self.daily_loss = 0.0
        self.last_trade_at = None
        self.exposure.clear()

    def evaluate_order(self, symbol: str, size_usd: float) -> Dict[str, Any]:
        reasons = []
        now = datetime.now(timezone.utc)
        cooldown = timedelta(seconds=self.config.cooldown_seconds)
        if self.last_trade_at and now - self.last_trade_at < cooldown:
            reasons.append("cooldown")
        total_capital = float(env_manager.get("TOTAL_CAPITAL_USDT", "0") or 0)
        exposure_limit = total_capital * self.config.max_exposure_pct
        exposure_after = self.exposure.get(symbol, 0.0) + size_usd
        if exposure_after > exposure_limit:
            reasons.append("exposure")
        daily_limit = float(env_manager.get("DAILY_INVEST_LIMIT_USDT", "0") or 0)
        if daily_limit and self.daily_loss >= daily_limit:
            reasons.append("daily_limit")
        allowed = not reasons
        return {"allowed": allowed, "reasons": reasons}

    def register_fill(self, symbol: str, pnl: float, size_usd: float) -> None:
        self.last_trade_at = datetime.now(timezone.utc)
        self.daily_loss += max(-pnl, 0)
        self.current_equity += pnl
        self.exposure[symbol] = max(self.exposure.get(symbol, 0.0) + size_usd, 0.0)
        if self.current_equity > self.max_equity:
            self.max_equity = self.current_equity

    def status(self) -> Dict[str, Any]:
        drawdown = 0.0
        if self.max_equity:
            drawdown = 1 - (self.current_equity / self.max_equity)
        return {
            "config": asdict(self.config),
            "daily_loss": self.daily_loss,
            "exposure": self.exposure,
            "drawdown": drawdown,
            "current_equity": self.current_equity,
        }

    def update_config(self, payload: Dict[str, Any]) -> RiskConfig:
        for field in payload:
            if hasattr(self.config, field):
                setattr(self.config, field, payload[field])
        return self.config


risk_manager = RiskManager()
