from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseBroker(ABC):
    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def simulate_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
