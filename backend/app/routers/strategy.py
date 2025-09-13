from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, Any, Dict
from backend.app.services.strategy_engine import run_dca

router = APIRouter(prefix="/api/strategy", tags=["strategy"])

class RunReq(BaseModel):
    kind: str
    user_id: str
    # 預留：若要一次性覆蓋設定，可附帶 params
    params: Optional[Dict[str,Any]] = None

@router.post("/run")
def run_strategy(req: RunReq):
    try:
        if req.kind.lower()=="dca":
            out = run_dca(req.user_id)
            return {"ok": True, "kind":"dca", "result": out}
        # 預留：breakout/grid
        return {"ok": False, "error":"unsupported_kind"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
