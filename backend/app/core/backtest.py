from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


def _random_walk(length: int, start: float = 100.0) -> List[Tuple[str, float]]:
    prices = [start]
    for _ in range(length - 1):
        change = random.gauss(0, 1)
        prices.append(max(prices[-1] * (1 + change / 100), 1))
    start_time = datetime.utcnow() - timedelta(minutes=length)
    return [((start_time + timedelta(minutes=i)).isoformat(), price) for i, price in enumerate(prices)]


def _equity_stats(equity: List[float]) -> Dict[str, float]:
    if len(equity) < 2:
        return {
            "sharpe": 0.0,
            "sortino": 0.0,
            "maxdd_pct": 0.0,
            "cagr": 0.0,
            "vol_annual": 0.0,
            "win_rate": 0.0,
            "trades": 0,
        }
    series = pd.Series(equity)
    returns = series.pct_change().dropna()
    downside = returns[returns < 0]
    sharpe = returns.mean() / (returns.std() + 1e-9) * math.sqrt(252)
    sortino = returns.mean() / (downside.std() + 1e-9) * math.sqrt(252)
    rolling_max = series.cummax()
    drawdowns = (series - rolling_max) / rolling_max
    maxdd = abs(drawdowns.min())
    total_return = series.iloc[-1] / max(series.iloc[0], 1e-9)
    years = len(series) / 252.0
    cagr = total_return ** (1 / max(years, 1e-9)) - 1
    vol_annual = returns.std() * math.sqrt(252)
    win_rate = float((returns > 0).mean())
    return {
        "sharpe": round(float(sharpe), 4),
        "sortino": round(float(sortino), 4),
        "maxdd_pct": round(float(maxdd), 4),
        "cagr": round(float(cagr), 4),
        "vol_annual": round(float(vol_annual), 4),
        "win_rate": round(win_rate, 4),
        "trades": len(returns),
    }


def _strategy_dca(prices: List[float], budget: float, every_n: int) -> List[float]:
    equity = []
    holdings = 0.0
    cash = budget
    for i, price in enumerate(prices):
        if i % every_n == 0 and cash > 0:
            spend = min(budget / 10, cash)
            holdings += spend / price
            cash -= spend
        equity.append(cash + holdings * price)
    return equity


def _strategy_breakout(prices: List[float], threshold: float = 1.02) -> List[float]:
    equity = []
    cash = prices[0]
    holdings = 0.0
    last_high = prices[0]
    for price in prices:
        if price > last_high * threshold and cash > 0:
            holdings += cash / price
            cash = 0
        elif price < last_high * 0.98 and holdings > 0:
            cash += holdings * price
            holdings = 0
        last_high = max(last_high, price)
        equity.append(cash + holdings * price)
    return equity


def _strategy_grid(prices: List[float], grid_size: int = 5, spread: float = 0.01) -> List[float]:
    equity = []
    cash = prices[0]
    holdings = 0.0
    base_price = prices[0]
    grid_levels = [base_price * (1 + spread * (i - grid_size // 2)) for i in range(grid_size)]
    for price in prices:
        for level in grid_levels:
            if price <= level and cash > 0:
                amount = cash * 0.1
                holdings += amount / price
                cash -= amount
            elif price >= level * 1.01 and holdings > 0:
                sell_amount = holdings * 0.1
                holdings -= sell_amount
                cash += sell_amount * price
        equity.append(cash + holdings * price)
    return equity


def run_backtest(payload: Dict[str, Any]) -> Dict[str, Any]:
    strategy = payload.get("strategy", "dca")
    params = payload.get("params", {})
    data = payload.get("data", {}).get("kline")
    if data:
        prices = [float(item[1]) if isinstance(item, (list, tuple)) else float(item) for item in data]
    else:
        length = int(params.get("lookback", 200))
        walk = _random_walk(length)
        prices = [price for _, price in walk]
        payload.setdefault("data", {})["kline"] = walk

    if strategy == "dca":
        budget = float(params.get("budget", 100))
        every_n = max(int(params.get("every_n", 5)), 1)
        equity = _strategy_dca(prices, budget, every_n)
    elif strategy == "breakout":
        threshold = float(params.get("threshold", 1.02))
        equity = _strategy_breakout(prices, threshold)
    else:
        grid_size = max(int(params.get("grid_size", 5)), 2)
        spread = float(params.get("spread", 0.01))
        equity = _strategy_grid(prices, grid_size, spread)

    stats = _equity_stats(equity)
    return {"equity": equity, "stats": stats, "data": payload.get("data")}


__all__ = ["run_backtest"]
