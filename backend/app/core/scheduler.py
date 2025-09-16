from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .ai import ai_engine
from .audit import log_event
from .cost import cost_manager
from .metrics import SCHEDULER_TICK_COUNTER


class AutopilotController:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.job = None
        self.state: Dict[str, Any] = {
            "active": False,
            "interval": 60,
            "last_run": None,
            "next_run": None,
            "last_error": None,
            "daily_cost": cost_manager.budget(),
            "last_model": None,
        }

    async def initialize(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    async def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        self.job = None
        self.state["active"] = False
        self.state["next_run"] = None

    async def _run_job(self) -> None:
        SCHEDULER_TICK_COUNTER.labels(job="autopilot").inc()
        self.state["last_run"] = datetime.now(timezone.utc).isoformat()
        try:
            result = await ai_engine.execute_autopilot()
            self.state["daily_cost"] = result.get("daily_cost", self.state["daily_cost"])
            self.state["last_model"] = result.get("model")
            self.state["last_decision"] = result.get("decision")
            self.state["last_orders"] = result.get("orders", [])
            log_event("autopilot_tick", result)
        except Exception as exc:  # pragma: no cover - safeguard
            self.state["last_error"] = str(exc)
            log_event("autopilot_error", {"error": str(exc)})
        finally:
            if self.job:
                next_run = self.job.next_run_time
                self.state["next_run"] = next_run.isoformat() if next_run else None

    async def start(self, interval: Optional[int] = None) -> Dict[str, Any]:
        await self.initialize()
        if interval:
            self.state["interval"] = interval
        if self.job:
            self.job.remove()
        self.job = self.scheduler.add_job(
            self._run_job,
            "interval",
            seconds=self.state["interval"],
            next_run_time=datetime.now(timezone.utc),
            coalesce=True,
            max_instances=1,
        )
        self.state["active"] = True
        next_run = self.job.next_run_time
        self.state["next_run"] = next_run.isoformat() if next_run else None
        log_event("autopilot_start", {"interval": self.state["interval"]})
        return self.state

    async def stop(self) -> Dict[str, Any]:
        if self.job:
            self.job.remove()
            self.job = None
        self.state["active"] = False
        self.state["next_run"] = None
        log_event("autopilot_stop")
        return self.state

    def status(self) -> Dict[str, Any]:
        return self.state


autopilot_controller = AutopilotController()
