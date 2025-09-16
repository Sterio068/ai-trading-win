from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np


def run_backtest(strategy: str, days: int = 30) -> Dict[str, any]:
    days = max(3, days)
    base_equity = 10000.0
    timestamps: List[str] = []
    equity_curve: List[float] = []
    returns = np.random.default_rng(seed=len(strategy) + days).normal(0.001, 0.01, days)
    if strategy.lower() == "breakout":
        returns += 0.0005
    elif strategy.lower() == "grid":
        returns *= 0.8
    equity = base_equity
    start = datetime.utcnow() - timedelta(days=days)
    for idx, r in enumerate(returns):
        equity *= (1 + r)
        timestamps.append((start + timedelta(days=idx)).isoformat())
        equity_curve.append(float(equity))
    total_return = equity_curve[-1] / base_equity - 1
    sharpe = float(np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252))
    max_drawdown = float(np.max(np.maximum.accumulate(equity_curve) - equity_curve) / np.max(equity_curve))
    return {
        "strategy": strategy,
        "equity": [{"ts": ts, "value": eq} for ts, eq in zip(timestamps, equity_curve)],
        "kpi": {
            "total_return": total_return,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
        },
    }
