import os, time, hmac, base64, hashlib, httpx, json, math
from typing import Any, Dict, Optional, List, Tuple
from backend.app.services.metrics import okx_requests_total, okx_latency
from backend.app.services.circuit import cb_okx
from backend.app.services.cache import cache_get, cache_set
from backend.app.svc import db as svc_db
from sqlalchemy import select, insert

OKX_BASE = os.getenv("OKX_BASE_URL","https://www.okx.com")
OKX_KEY  = os.getenv("OKX_API_KEY","")
OKX_SECRET = os.getenv("OKX_API_SECRET","")
OKX_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE","")
OKX_SIM = os.getenv("OKX_SIMULATED","1") in ("1","true","True","YES","yes")
FEATURE_IDEMP = os.getenv("FEATURE_IDEMPOTENCY","1") in ("1","true","True")
FEATURE_CACHE_INSTRUMENT = os.getenv("FEATURE_CACHE_INSTRUMENT","1") in ("1","true","True")

_clock_offset_ms = 0

def _iso(ts_ms: int) -> str:
    s, ms = divmod(ts_ms, 1000); return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s)) + f".{ms:03d}Z"

def _now_ms()->int:
    return int(time.time()*1000) + _clock_offset_ms

def _sign(prehash: str) -> str:
    return base64.b64encode(hmac.new(OKX_SECRET.encode(), prehash.encode(), hashlib.sha256).digest()).decode()

def _headers(c: httpx.Client, method: str, path: str, body: str="") -> Dict[str,str]:
    ts_ms = _now_ms()
    ts = _iso(ts_ms)
    h = {
        "OK-ACCESS-KEY": OKX_KEY,
        "OK-ACCESS-SIGN": _sign(f"{ts}{method.upper()}{path}{body}"),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
        "Content-Type": "application/json",
    }
    if OKX_SIM: h["x-simulated-trading"]="1"
    if FEATURE_IDEMP and method.upper()=="POST": h["Idempotency-Key"]=str(ts_ms)
    return h

def _sync_clock(c: httpx.Client):
    global _clock_offset_ms
    try:
        t0 = int(time.time()*1000)
        srv = c.get("/api/v5/public/time").json()
        ts = int(srv["data"][0]["ts"])
        t1 = int(time.time()*1000)
        rtt = (t1 - t0)//2
        _clock_offset_ms = ts - (t0 + rtt)
    except Exception:
        pass

def _okx(method:str, path:str, params:Dict[str,Any]|None=None, body:Dict[str,Any]|None=None)->Dict[str,Any]:
    if not cb_okx.allow():
        return {"ok":False,"error":"circuit_open"}
    t = okx_latency.labels(method, path).time()
    try:
        with httpx.Client(base_url=OKX_BASE, timeout=20) as c:
            _sync_clock(c)
            if method=="GET":
                r = c.get(path, headers=_headers(c,"GET",path), params=params)
            else:
                b = json.dumps(body or {}, separators=(",",":"))
                r = c.post(path, headers=_headers(c,"POST",path,b), content=b)
            st=str(r.status_code)
            okx_requests_total.labels(method, path, st).inc()
            r.raise_for_status()
            cb_okx.on_success()
            return r.json()
    except Exception as e:
        cb_okx.on_error()
        okx_requests_total.labels(method, path, "error").inc()
        return {"ok":False,"error":str(e)}
    finally:
        t.observe_duration()

def okx_get(path:str, params:Dict[str,Any]|None=None)->Dict[str,Any]:
    return _okx("GET", path, params=params)

def okx_post(path:str, body:Dict[str,Any])->Dict[str,Any]:
    return _okx("POST", path, body=body)

def get_instrument(inst:str, instType:str)->Tuple[Dict[str,Any], float, float, float, float, float]:
    """return (info, minSz, lotSz, tickSz, ctVal, ctMult)"""
    cache_key = f"ins:{instType}:{inst}"
    if FEATURE_CACHE_INSTRUMENT:
        cv = cache_get(cache_key)
        if cv:
            d=json.loads(cv)
            info=d["info"]; return info, d["minSz"], d["lotSz"], d["tickSz"], d["ctVal"], d["ctMult"]
    r = okx_get("/api/v5/public/instruments", {"instType":instType,"instId":inst})
    info = (r.get("data") or [None])[0] or {}
    minSz=float(info.get("minSz") or 0.01); lotSz=float(info.get("lotSz") or minSz); tickSz=float(info.get("tickSz") or 0.1)
    ctVal=float(info.get("ctVal") or 0.0); ctMult=float(info.get("ctMult") or 1.0)
    if FEATURE_CACHE_INSTRUMENT:
        cache_set(cache_key, {"info":info,"minSz":minSz,"lotSz":lotSz,"tickSz":tickSz,"ctVal":ctVal,"ctMult":ctMult}, ttl=30)
    return info, minSz, lotSz, tickSz, ctVal, ctMult

def get_ticker(instId:str)->float:
    r = okx_get("/api/v5/market/ticker", {"instId":instId})
    return float(((r.get("data") or [{}])[0]).get("last") or 0)

def place_spot_market_quote(instId:str, quote_budget:float)->Dict[str,Any]:
    body={"instId":instId,"tdMode":"cash","side":"buy","ordType":"market","tgtCcy":"quote_ccy","sz":str(round(float(quote_budget),6))}
    return okx_post("/api/v5/trade/order", body)

def place_swap_market(instId:str, sz:float, side:str="buy", posSide:str="long", tdMode:str="cross")->Dict[str,Any]:
    body={"instId":instId,"tdMode":tdMode,"side":side,"posSide":posSide,"ordType":"market","sz":str(int(sz) if float(sz).is_integer() else sz)}
    return okx_post("/api/v5/trade/order", body)

def est_min_notional(instType:str, minSz:float, last:float, ctVal:float, ctMult:float)->float:
    return (minSz*last) if instType=="SPOT" else (minSz*ctVal*ctMult*last)
