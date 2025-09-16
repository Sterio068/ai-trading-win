from __future__ import annotations

import math
from typing import Any, Dict, List

from .env import env_floats
from .metrics import allocator_rebalance_total

CANDIDATE_PAIRS = [
    {"instId": "BTC-USDT", "vol": 0.6},
    {"instId": "ETH-USDT", "vol": 0.7},
    {"instId": "SOL-USDT", "vol": 0.9},
    {"instId": "XRP-USDT", "vol": 1.1},
]


def _risk_parity_weights(volatility: List[float]) -> List[float]:
    inv_vol = [1.0 / max(v, 1e-6) for v in volatility]
    total = sum(inv_vol)
    if total == 0:
        return [1.0 / len(volatility)] * len(volatility)
    return [w / total for w in inv_vol]


def plan_allocation(vol_multiplier: float = 1.0) -> Dict[str, Any]:
    numbers = env_floats(
        [
            ("TOTAL_CAPITAL_USDT", 10000.0),
            ("DAILY_INVEST_LIMIT_USDT", 500.0),
            ("SINGLE_TRADE_LIMIT_USDT", 50.0),
        ]
    )
    total_capital = numbers["TOTAL_CAPITAL_USDT"]
    daily_limit = min(numbers["DAILY_INVEST_LIMIT_USDT"], total_capital)
    single_limit = min(numbers["SINGLE_TRADE_LIMIT_USDT"], daily_limit)

    selected = CANDIDATE_PAIRS[:3]
    vols = [max(item["vol"] * vol_multiplier, 0.2) for item in selected]
    weights = _risk_parity_weights(vols)

    allocations = []
    for item, weight in zip(selected, weights):
        notional = round(daily_limit * weight, 2)
        allocations.append(
            {
                "instId": item["instId"],
                "weight": weight,
                "notional": notional,
            }
        )

    base_interval = max(60, math.floor(3600 / (1 + daily_limit / max(single_limit, 1))))
    allocator_rebalance_total.inc()
    return {
        "total_capital": total_capital,
        "daily_limit": daily_limit,
        "single_trade_limit": single_limit,
        "allocations": allocations,
        "suggested_interval_s": base_interval,
    }


__all__ = ["plan_allocation"]
