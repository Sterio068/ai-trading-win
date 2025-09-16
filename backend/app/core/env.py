from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Tuple

from pydantic import BaseModel

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

DEFAULT_ENV: Dict[str, str] = {
    "MODE": "paper",
    "EXCHANGE_ACTIVE": "okx",
    "OPENAI_MODEL_TIER": "gpt-5-nano",
    "OKX_API_KEY_PAPER": "",
    "OKX_API_SECRET_PAPER": "",
    "OKX_PASSPHRASE_PAPER": "",
    "OKX_API_KEY_REAL": "",
    "OKX_API_SECRET_REAL": "",
    "OKX_PASSPHRASE_REAL": "",
    "SENTRY_DSN": "",
    "AI_DAILY_COST_LIMIT_USD": "3.0",
    "DAILY_INVEST_LIMIT_USDT": "500",
    "SINGLE_TRADE_LIMIT_USDT": "50",
    "TOTAL_CAPITAL_USDT": "10000",
}


class EnvWriteResult(BaseModel):
    diff: Dict[str, Tuple[str, str]]


def ensure_env_file() -> None:
    if not ENV_PATH.exists():
        ENV_PATH.write_text("\n".join(f"{k}={v}" for k, v in DEFAULT_ENV.items()) + "\n", encoding="utf-8")
    else:
        # Ensure defaults exist without overriding user values
        current = read_env()
        changed = False
        for key, value in DEFAULT_ENV.items():
            if key not in current:
                current[key] = value
                changed = True
        if changed:
            write_env(current)


def read_env() -> Dict[str, str]:
    ensure_env_file()
    data: Dict[str, str] = {}
    with ENV_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def mask_value(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"


def masked_env() -> Dict[str, str]:
    env = read_env()
    return {key: mask_value(value) for key, value in env.items()}


def _render_env(env_dict: Dict[str, str]) -> str:
    lines = [f"{key}={value}" for key, value in env_dict.items()]
    return "\n".join(lines) + "\n"


def write_env(env_dict: Dict[str, str]) -> None:
    ENV_PATH.write_text(_render_env(env_dict), encoding="utf-8")
    for key, value in env_dict.items():
        os.environ[key] = value


def update_env(updates: Dict[str, str]) -> EnvWriteResult:
    current = read_env()
    diff: Dict[str, Tuple[str, str]] = {}
    for key, value in updates.items():
        old = current.get(key, "")
        if value is None:
            value = ""
        if old != value:
            diff[key] = (old, value)
            current[key] = value
    write_env(current)
    return EnvWriteResult(diff=diff)


def switch_mode(mode: str) -> EnvWriteResult:
    if mode not in {"paper", "real"}:
        raise ValueError("mode must be 'paper' or 'real'")
    return update_env({"MODE": mode})


def env_floats(keys: Iterable[Tuple[str, float]]) -> Dict[str, float]:
    env = read_env()
    results: Dict[str, float] = {}
    for key, default in keys:
        try:
            results[key] = float(env.get(key, default))
        except (TypeError, ValueError):
            results[key] = default
    return results


def get_env_value(key: str, default: str = "") -> str:
    env = read_env()
    return env.get(key, default)


ensure_env_file()
