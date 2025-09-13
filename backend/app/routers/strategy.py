from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, Any, Dict
from backend.app.services.strategy_engine import run_dca

router = APIRouter(prefix="/api/strategy", tags=["strategy"])

class RunReq(BaseModel):
    kind: str
    user_id: str
    # Optional override parameters for one-off execution
    params: Optional[Dict[str, Any]] = None

@router.post("/run")
def run_strategy(req: RunReq):
    """Trigger a trading strategy for the given user."""
    try:
        if req.kind.lower() == "dca":
            out = run_dca(req.user_id)
            return {"ok": True, "kind": "dca", "result": out}
        # Placeholder for future strategies (breakout, grid, etc.)
        return {"ok": False, "error": "unsupported_kind"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
