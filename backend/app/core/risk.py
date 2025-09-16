from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from .metrics import guard_block_total, guard_pass_total

RISK_CONFIG_PATH = Path(__file__).resolve().parents[2] / "storage" / "risk_config.json"
RISK_STATE_PATH = Path(__file__).resolve().parents[2] / "storage" / "risk_state.json"
RISK_VERSION_PATH = Path(__file__).resolve().parents[2] / "storage" / "risk_versions.json"

DEFAULT_CONFIG = {
    "daily_loss_cap": 100.0,
    "max_exposure_per_symbol": 200.0,
    "cooldown_sec": 20,
    "sl_tp": {
        "sl_pct": 0.01,
        "tp_pct": 0.02,
        "trail_pct": 0.0,
        "tp_steps": [],
    },
    "dynamic_sizing": {
        "base_usdt": 10.0,
        "risk_scale": 1.0,
    },
    "volatility": {
        "use": True,
        "min_mult": 0.6,
        "max_mult": 1.4,
    },
    "kelly_cap": 0.05,
    "max_dd_stop": 0.10,
}

DEFAULT_STATE = {
    "realized_pnl": 0.0,
    "symbol_exposure": {},
    "last_order_ts": {},
    "equity_peak": 0.0,
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return deepcopy(default)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


class RiskManager:
    def __init__(self) -> None:
        self._config = _load_json(RISK_CONFIG_PATH, {"version": 1, "updated_by": "system", "updated_at": datetime.utcnow().isoformat(), "config": DEFAULT_CONFIG})
        self._state = _load_json(RISK_STATE_PATH, DEFAULT_STATE)
        if "config" not in self._config:
            self._config = {"version": 1, "updated_by": "system", "updated_at": datetime.utcnow().isoformat(), "config": DEFAULT_CONFIG}
            self._persist_config(self._config)
        if not RISK_VERSION_PATH.exists():
            _save_json(RISK_VERSION_PATH, [self._version_entry({}, DEFAULT_CONFIG)])

    def _version_entry(self, diff: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "version": self._config.get("version", 1),
            "updated_by": self._config.get("updated_by", "system"),
            "updated_at": self._config.get("updated_at", datetime.utcnow().isoformat()),
            "diff": diff,
            "config": config,
        }

    def _persist_config(self, data: Dict[str, Any]) -> None:
        _save_json(RISK_CONFIG_PATH, data)

    def _persist_state(self) -> None:
        _save_json(RISK_STATE_PATH, self._state)

    @property
    def config(self) -> Dict[str, Any]:
        return deepcopy(self._config.get("config", DEFAULT_CONFIG))

    def get_state(self) -> Dict[str, Any]:
        return deepcopy(self._state)

    def get_version_info(self) -> Dict[str, Any]:
        versions = _load_json(RISK_VERSION_PATH, [])
        if versions:
            latest = versions[-1]
            return {
                "version": latest.get("version"),
                "updated_by": latest.get("updated_by"),
                "updated_at": latest.get("updated_at"),
                "diff": latest.get("diff"),
            }
        return {
            "version": self._config.get("version", 1),
            "updated_by": self._config.get("updated_by", "system"),
            "updated_at": self._config.get("updated_at", datetime.utcnow().isoformat()),
            "diff": {},
        }

    def _diff_config(self, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        diff: Dict[str, Any] = {}
        for key in set(old.keys()).union(new.keys()):
            if old.get(key) != new.get(key):
                diff[key] = {"old": old.get(key), "new": new.get(key)}
        return diff

    def update_config(self, new_config: Dict[str, Any], updated_by: str = "system") -> Dict[str, Any]:
        old_config = self.config
        merged = deepcopy(old_config)
        merged.update(new_config)
        version = int(self._config.get("version", 1)) + 1
        record = {
            "version": version,
            "updated_by": updated_by,
            "updated_at": datetime.utcnow().isoformat(),
            "config": merged,
        }
        diff = self._diff_config(old_config, merged)
        self._config = record
        self._persist_config(record)
        history = _load_json(RISK_VERSION_PATH, [])
        history.append({"version": version, "updated_by": updated_by, "updated_at": record["updated_at"], "diff": diff})
        _save_json(RISK_VERSION_PATH, history)
        return {"version": version, "diff": diff}

    def _ensure_peak(self, equity: float) -> None:
        peak = float(self._state.get("equity_peak", 0.0))
        if equity > peak:
            self._state["equity_peak"] = equity
            self._persist_state()

    def guard(self, *, symbol: str, notional: float, now: float, equity: float) -> Tuple[bool, str]:
        config = self.config
        state = self._state
        self._ensure_peak(equity)
        peak = float(state.get("equity_peak", equity)) or equity
        if peak <= 0:
            peak = equity if equity > 0 else config["daily_loss_cap"] * 2
        dd = 0.0
        if peak > 0:
            dd = max((peak - equity) / peak, 0.0)
        if dd >= config.get("max_dd_stop", 0.1):
            guard_block_total.labels(reason="DD").inc()
            return False, "RISK_DD_STOP"

        realized = float(state.get("realized_pnl", 0.0))
        if realized <= -abs(config.get("daily_loss_cap", 100.0)):
            guard_block_total.labels(reason="CAP").inc()
            return False, "RISK_DAILY_CAP"

        exposures = state.setdefault("symbol_exposure", {})
        current_expo = float(exposures.get(symbol, 0.0))
        max_expo = float(config.get("max_exposure_per_symbol", 200.0))
        if current_expo + abs(notional) > max_expo:
            guard_block_total.labels(reason="EXPO").inc()
            return False, "RISK_EXPOSURE_LIMIT"

        cooldowns = state.setdefault("last_order_ts", {})
        last_ts = float(cooldowns.get(symbol, 0.0))
        cooldown_sec = int(config.get("cooldown_sec", 20))
        if now - last_ts < cooldown_sec:
            guard_block_total.labels(reason="COOL").inc()
            remaining = cooldown_sec - (now - last_ts)
            return False, f"RISK_COOLDOWN:{remaining:.0f}s"

        guard_pass_total.labels(reason="ok").inc()
        return True, "ok"

    def on_order_commit(self, *, symbol: str, notional: float, now: float) -> None:
        exposures = self._state.setdefault("symbol_exposure", {})
        exposures[symbol] = float(exposures.get(symbol, 0.0)) + abs(notional)
        self._state.setdefault("last_order_ts", {})[symbol] = now
        self._persist_state()

    def on_fill(self, *, symbol: str, pnl: float, notional: float = 0.0) -> None:
        exposures = self._state.setdefault("symbol_exposure", {})
        exposures[symbol] = max(float(exposures.get(symbol, 0.0)) - abs(notional), 0.0)
        self._state["realized_pnl"] = float(self._state.get("realized_pnl", 0.0)) + pnl
        self._persist_state()

    def reset_daily(self) -> None:
        self._state["realized_pnl"] = 0.0
        self._state["last_order_ts"] = {}
        self._persist_state()


risk_manager = RiskManager()


__all__ = ["risk_manager", "RiskManager", "DEFAULT_CONFIG"]
