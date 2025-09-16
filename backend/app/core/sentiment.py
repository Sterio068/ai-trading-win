from __future__ import annotations

import re
from typing import Dict

POSITIVE = {"bullish", "buy", "long", "positive", "up"}
NEGATIVE = {"bearish", "sell", "short", "negative", "down"}


def aggregate_sentiment(text: str) -> Dict[str, float]:
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    pos = sum(1 for token in tokens if token in POSITIVE)
    neg = sum(1 for token in tokens if token in NEGATIVE)
    total = max(len(tokens), 1)
    score = (pos - neg) / total
    label = "neutral"
    if score > 0.1:
        label = "bullish"
    elif score < -0.1:
        label = "bearish"
    return {"label": label, "score": score, "tokens": len(tokens)}
