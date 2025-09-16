from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"

DEFAULT_ENV: Dict[str, str] = {
    "MODE": "PAPER",
    "EXCHANGE_ACTIVE": "OKX",
    "OPENAI_MODEL_TIER": "GPT-5-MINI",
    "OPENAI_API_KEY": "",
    "CORS_ALLOW_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
    "OKX_API_KEY_PAPER": "",
    "OKX_API_SECRET_PAPER": "",
    "OKX_API_PASSPHRASE_PAPER": "",
    "OKX_API_KEY_REAL": "",
    "OKX_API_SECRET_REAL": "",
    "OKX_API_PASSPHRASE_REAL": "",
    "SENTRY_DSN": "",
    "AI_DAILY_COST_LIMIT_USD": "50",
    "DAILY_INVEST_LIMIT_USDT": "5000",
    "SINGLE_TRADE_LIMIT_USDT": "1000",
    "TOTAL_CAPITAL_USDT": "20000",
}


class EnvManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._env: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._env = DEFAULT_ENV.copy()
            self.write(DEFAULT_ENV)
        else:
            values = dotenv_values(self.path)
            merged = DEFAULT_ENV.copy()
            merged.update({k: v for k, v in values.items() if v is not None})
            self._env = merged

    def get(self, key: str, default: Optional[str] = None) -> str:
        return self._env.get(key, default or "")

    @property
    def mode(self) -> str:
        return self.get("MODE", "PAPER")

    def write(self, updates: Dict[str, str]) -> Dict[str, str]:
        self._env.update(updates)
        lines = [f"{key}={self._env.get(key, '')}" for key in sorted(DEFAULT_ENV.keys())]
        with self.path.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        os.environ.update(self._env)
        return self._env

    def update_env(self, payload: Dict[str, str]) -> Dict[str, str]:
        clean_payload = {k: v for k, v in payload.items() if k in DEFAULT_ENV}
        return self.write(clean_payload)

    def switch_mode(self, mode: str) -> Dict[str, str]:
        mode = mode.upper()
        if mode not in {"PAPER", "REAL"}:
            raise ValueError("mode must be PAPER or REAL")
        return self.write({"MODE": mode})

    def masked_env(self) -> Dict[str, str]:
        masked: Dict[str, str] = {}
        for key, value in self._env.items():
            if "KEY" in key or "SECRET" in key or "PASSPHRASE" in key:
                masked[key] = self._mask(value)
            else:
                masked[key] = value
        return masked

    @staticmethod
    def _mask(value: str) -> str:
        if not value:
            return ""
        visible = value[-4:] if len(value) > 4 else value
        return f"***{visible}"


env_manager = EnvManager(ENV_PATH)
