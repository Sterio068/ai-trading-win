from __future__ import annotations

from typing import Dict, Iterable

POSITIVE_WORDS = {"bull", "up", "gain", "positive", "moon", "profit"}
NEGATIVE_WORDS = {"bear", "down", "loss", "negative", "risk", "selloff"}


def score_texts(texts: Iterable[str]) -> Dict[str, float]:
    total = 0
    pos_hits = 0
    neg_hits = 0
    for text in texts:
        words = text.lower().split()
        total += len(words)
        pos_hits += sum(1 for w in words if w in POSITIVE_WORDS)
        neg_hits += sum(1 for w in words if w in NEGATIVE_WORDS)
    if total == 0:
        return {"score": 0.0, "positive": 0, "negative": 0, "summary": "neutral"}
    score = (pos_hits - neg_hits) / max(total, 1)
    summary = "neutral"
    if score > 0.05:
        summary = "positive"
    elif score < -0.05:
        summary = "negative"
    return {
        "score": round(score, 4),
        "positive": pos_hits,
        "negative": neg_hits,
        "summary": summary,
    }


__all__ = ["score_texts"]
