from __future__ import annotations

from typing import Dict, List


class PortfolioAllocator:
    def allocate(self, universe: List[str], capital: float) -> List[Dict[str, float]]:
        if not universe:
            return []
        weight = 1 / len(universe)
        return [{"symbol": symbol, "allocation": round(capital * weight, 2)} for symbol in universe]


allocator = PortfolioAllocator()
