from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class Broker(ABC):
    @abstractmethod
    async def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_algo_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def batch_orders(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_open_orders(self, inst_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_fills_history(self, inst_id: str, start: str | None, end: str | None) -> Dict[str, Any]:
        raise NotImplementedError


__all__ = ["Broker"]
