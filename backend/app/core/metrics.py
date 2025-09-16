from __future__ import annotations

from prometheus_client import Counter, Gauge

order_submit_total = Counter(
    "order_submit_total", "Total order submissions", ["exchange", "mode"]
)
order_submit_success = Counter(
    "order_submit_success", "Successful order submissions", ["exchange", "mode"]
)
order_submit_reject = Counter(
    "order_submit_reject", "Rejected orders", ["exchange", "mode", "code"]
)
guard_pass_total = Counter(
    "guard_pass_total", "Guards passed", ["reason"]
)
guard_block_total = Counter(
    "guard_block_total", "Guards blocked", ["reason"]
)
ai_calls_total = Counter("ai_calls_total", "AI calls", ["tier"])
ai_cost_usd_total = Counter("ai_cost_usd_total", "AI cost in USD", ["tier"])
ai_budget_left_usd = Gauge("ai_budget_left_usd", "AI budget left in USD")
allocator_rebalance_total = Counter(
    "allocator_rebalance_total", "Allocator rebalance operations"
)
ws_messages_total = Counter("ws_messages_total", "Websocket messages", ["topic"])
scheduler_runs_total = Counter("scheduler_runs_total", "Scheduler job runs", ["job"])
backend_info = Gauge("backend_info", "Backend build information", ["version"])
backend_info.labels(version="1.2.0").set(1)


__all__ = [name for name in globals() if name.isidentifier()]
