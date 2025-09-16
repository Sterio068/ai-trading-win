from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .cost import get_cost_snapshot
from .metrics import scheduler_runs_total

AUTOPILOT_STATE_PATH = Path(__file__).resolve().parents[2] / "storage" / "autopilot.json"

_scheduler = AsyncIOScheduler()
_strategy_executor: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None
_autopilot_lock = asyncio.Lock()


def _load_state() -> Dict[str, Any]:
    if not AUTOPILOT_STATE_PATH.exists():
        return {
            "running": False,
            "base_interval_s": 120,
            "last_tick": None,
            "tier_stats": {},
            "cost_today": {},
        }
    with AUTOPILOT_STATE_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_state(state: Dict[str, Any]) -> None:
    AUTOPILOT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUTOPILOT_STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def register_strategy_executor(callback: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]) -> None:
    global _strategy_executor
    _strategy_executor = callback


async def autopilot_tick() -> None:
    async with _autopilot_lock:
        state = _load_state()
        if not state.get("running"):
            return
        scheduler_runs_total.labels(job="autopilot_tick").inc()
        payload = {"mode": "autopilot", "instId": state.get("instId")}
        result: Dict[str, Any] = {}
        if _strategy_executor:
            result = await _strategy_executor(payload)
        state["last_tick"] = datetime.utcnow().isoformat()
        if result:
            state["last_result"] = result
            if "next_interval_s" in result:
                state["next_interval_s"] = result["next_interval_s"]
        cost_snapshot = get_cost_snapshot()
        state["cost_today"] = cost_snapshot
        _save_state(state)
        next_interval = result.get("next_interval_s") if result else None
        if not next_interval:
            next_interval = state.get("base_interval_s", 120)
        schedule_autopilot(next_interval)


def start_scheduler() -> None:
    if not _scheduler.running:
        _scheduler.start()


def shutdown_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


def schedule_autopilot(interval_seconds: float) -> None:
    if interval_seconds <= 0:
        interval_seconds = 60
    run_time = datetime.utcnow() + timedelta(seconds=interval_seconds)
    _scheduler.add_job(
        lambda: asyncio.create_task(autopilot_tick()),
        "date",
        run_date=run_time,
        id="autopilot_tick",
        replace_existing=True,
    )


def set_autopilot_state(running: bool, base_interval: float, inst_id: Optional[str] = None) -> Dict[str, Any]:
    state = _load_state()
    state["running"] = running
    state["base_interval_s"] = base_interval
    state["cost_today"] = get_cost_snapshot()
    if inst_id is not None:
        state["instId"] = inst_id
    if not running:
        state.pop("next_interval_s", None)
    _save_state(state)
    if running:
        schedule_autopilot(base_interval)
    else:
        
        if _scheduler.running:
            _scheduler.remove_all_jobs()
    return state


def get_autopilot_state() -> Dict[str, Any]:
    return _load_state()


__all__ = [
    "start_scheduler",
    "shutdown_scheduler",
    "schedule_autopilot",
    "register_strategy_executor",
    "set_autopilot_state",
    "get_autopilot_state",
    "autopilot_tick",
]
