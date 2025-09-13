from fastapi import APIRouter, Query, Request, Response, HTTPException
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel
from sqlalchemy import select, insert, update
from backend.app.svc import db as svc_db
from backend.app.services import okx_core as okx
from backend.app.services.strategy_engine import run_dca
from backend.app.services.cache import make_etag, cache_get, cache_set
from backend.app.services.metrics import http_requests_total, http_latency

router = APIRouter()

# ---------- AI 設定 ----------
class SettingIn(BaseModel):
    user_id: str; key: str; data: Dict[str, Any]

@router.post("/api/ai/settings")
async def upsert_setting(payload: SettingIn):
    await svc_db.init_pool()
    # SQLite 兼容 upsert：先 update，沒更新到再 insert
    upd = update(svc_db.ai_settings).where(
        (svc_db.ai_settings.c.user_id==payload.user_id) & (svc_db.ai_settings.c.key==payload.key)
    ).values(data=payload.data)
    rc = await svc_db.db.execute(upd)
    if not rc:
        await svc_db.db.execute(insert(svc_db.ai_settings).values(
            user_id=payload.user_id, key=payload.key, data=payload.data
        ))
    return {"ok": True}

@router.get("/api/ai/settings")
async def list_settings(user_id: str = Query(...)):
    await svc_db.init_pool()
    rows = await svc_db.db.fetch_all(select(svc_db.ai_settings).where(svc_db.ai_settings.c.user_id==user_id))
    out={}
    for r in rows: out[r["key"]] = r["data"]
    return {"rows": out}

# ---------- 風控 ----------
class LimitsIn(BaseModel):
    user_id: str
    max_notional_per_symbol: Optional[float]=0
    max_total_notional: Optional[float]=0
    daily_loss_stop: Optional[float]=0
    window: str="00:00-23:59"

@router.post("/api/risk/limits")
async def set_limits(payload: LimitsIn):
    await svc_db.init_pool()
    v = {"user_id":payload.user_id,"max_symbol":float(payload.max_notional_per_symbol or 0),
         "max_total":float(payload.max_total_notional or 0),"daily_loss":float(payload.daily_loss_stop or 0),
         "window":payload.window}
    upd = update(svc_db.risk_limits).where(svc_db.risk_limits.c.user_id==payload.user_id).values(**v)
    rc = await svc_db.db.execute(upd)
    if not rc: await svc_db.db.execute(insert(svc_db.risk_limits).values(**v))
    return {"ok":True}

@router.get("/api/risk/limits")
async def get_limits(user_id: str):
    await svc_db.init_pool()
    row = await svc_db.db.fetch_one(select(svc_db.risk_limits).where(svc_db.risk_limits.c.user_id==user_id))
    if not row: return {"user_id":user_id,"max_symbol":0.0,"max_total":0.0,"daily_loss":0.0,"window":"00:00-23:59"}
    return {"user_id":row["user_id"],"max_symbol":float(row["max_symbol"]),
            "max_total":float(row["max_total"]),"daily_loss":float(row["daily_loss"]),"window":row["window"]}

# ---------- Sentiment ----------
@router.post("/api/sentiment/put")
async def put_sent(symbol: str, score: float):
    await svc_db.init_pool()
    await svc_db.db.execute(insert(svc_db.sentiment).values(symbol=symbol, score=float(score)))
    return {"ok":True,"symbol":symbol,"score":float(score)}

@router.get("/api/sentiment/score")
async def get_score(symbol: str):
    await svc_db.init_pool()
    rows = await svc_db.db.fetch_all(select(svc_db.sentiment.c.score).where(svc_db.sentiment.c.symbol==symbol).order_by(svc_db.sentiment.c.ts.desc()).limit(10))
    if not rows: return {"symbol":symbol,"score":0.0,"source_count":0}
    vals=[float(r["score"]) for r in rows]
    return {"symbol":symbol,"score":sum(vals)/len(vals),"source_count":len(vals)}

# ---------- OKX 包裝 ----------
@router.get("/api/okx/instrument")
def instrument(req: Request, res: Response, inst: str, instType: str, notional: float|None=None):
    it=instType.upper()
    info,minSz,lotSz,tickSz,ctVal,ctMult = okx.get_instrument(inst, it)
    last = okx.get_ticker(inst)
    minNotional = okx.est_min_notional(it, minSz, last, ctVal, ctMult)
    payload = {
        "instId":inst,"instType":it,"found":bool(info),
        "instrument":{"baseCcy":info.get("baseCcy",""),"quoteCcy":info.get("quoteCcy",""),
                      "state":info.get("state",""),"ctVal":str(info.get("ctVal","") or ""),
                      "ctMult":str(info.get("ctMult","") or "1"),"uly":info.get("uly",""),"listTime":info.get("listTime","")},
        "rules":{"minSz":minSz,"lotSz":lotSz,"tickSz":tickSz,"minNotional":round(minNotional,6)},
        "price":{"last":last,"ask":last,"bid":last,"markPx":last,"indexPx":last,"basePx":last},
        "ui_hint": f"最低名目金額：{minNotional:.2f} USDT（minSz={minSz}, tickSz={tickSz}" + (f", ctVal={ctVal}" if it!="SPOT" else "") + "）"
    }
    # ETag
    if os.getenv("FEATURE_HTTP_CACHE_ETAG","1") in ("1","true","True"):
        etag = make_etag(payload)
        inm = req.headers.get("if-none-match")
        res.headers["ETag"]=etag
        if inm and inm==etag:
            res.status_code=304
            return {}
    if notional is not None:
        ok = float(notional) >= float(minNotional)
        payload["notional_check"]={"input":float(notional),"ok":ok,"reason":"" if ok else "Below minimal notional"}
    return payload

@router.post("/api/okx/place-order")
def place_order(body: Dict[str,Any]):
    return okx.okx_post("/api/v5/trade/order", body)

@router.post("/api/okx/cancel")
def cancel_order(body: Dict[str,Any]):
    return okx.okx_post("/api/v5/trade/cancel-order", body)

@router.get("/api/okx/order")
def get_order(instId: str, ordId: str):
    return okx.okx_get("/api/v5/trade/order", {"instId":instId,"ordId":ordId})

@router.get("/api/okx/orders-pending")
def orders_pending(instType: str|None=None, instId: str|None=None):
    params={}; 
    if instType: params["instType"]=instType
    if instId: params["instId"]=instId
    return okx.okx_get("/api/v5/trade/orders-pending", params)

@router.get("/api/okx/orders-history")
def orders_history(instType: str, instId: str|None=None, state: str|None=None, limit:int=20):
    p={"instType":instType,"limit":str(limit)}
    if instId: p["instId"]=instId
    if state: p["state"]=state
    return okx.okx_get("/api/v5/trade/orders-history", p)

# ---------- 一鍵 AI 交易 ----------
class RunIn(BaseModel):
    kind: Literal["dca","breakout","grid"]
    user_id: str

@router.post("/api/strategy/run")
async def run_strategy(payload: RunIn):
    await svc_db.init_pool()
    # 目前完整串 DCA（SPOT=budget / SWAP=sz），其他策略可類推填入 engine
    rows = await svc_db.db.fetch_all(select(svc_db.ai_settings).where(svc_db.ai_settings.c.user_id==payload.user_id))
    m={}; [m.update({r["key"]:r["data"]}) for r in rows]
    m["_user_id"]=payload.user_id
    if payload.kind=="dca":
        return await run_dca(m)
    return {"ok":False,"reason":"not_implemented"}

# ---------- 量測中介（可視需要包住所有路由） ----------
@router.middleware("http")
async def _metrics_mw(request: Request, call_next):
    path = request.url.path; mth = request.method
    with http_latency.labels(mth, path).time():
        resp = await call_next(request)
    http_requests_total.labels(mth, path, str(resp.status_code)).inc()
    return resp
