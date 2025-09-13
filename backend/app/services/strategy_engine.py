import os, time, hmac, hashlib, base64, json, math
from typing import Dict, Any, List, Optional, Tuple
import httpx

OKX_BASE   = os.getenv("OKX_BASE_URL", "https://www.okx.com")
OKX_KEY    = os.getenv("OKX_API_KEY")
OKX_SEC    = os.getenv("OKX_API_SECRET")
OKX_PAS    = os.getenv("OKX_API_PASSPHRASE")
OKX_SIM    = os.getenv("OKX_SIMULATED", "0") in ("1","true","True","YES","yes")

def _iso(ts_ms:int)->str:
    s, ms = divmod(int(ts_ms), 1000)
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s)) + f".{ms:03d}Z"

def _okx_headers(c:httpx.Client, method:str, path:str, body:str="")->Dict[str,str]:
    ts = int(c.get("/api/v5/public/time").json()["data"][0]["ts"])
    iso = _iso(ts)
    pre = f"{iso}{method.upper()}{path}{body}"
    sig = base64.b64encode(hmac.new(OKX_SEC.encode(), pre.encode(), hashlib.sha256).digest()).decode()
    h = {
        "OK-ACCESS-KEY":OKX_KEY,
        "OK-ACCESS-SIGN":sig,
        "OK-ACCESS-TIMESTAMP":iso,
        "OK-ACCESS-PASSPHRASE":OKX_PAS,
        "Content-Type":"application/json",
    }
    if OKX_SIM:
        h["x-simulated-trading"]="1"
    return h

def _place_order_spot_market_quote(instId:str, quote_amount:float, side:str="buy")->Dict[str,Any]:
    """以 USDT 名目下 **SPOT 市價單**（OKX 需使用 tgtCcy=quote_ccy）"""
    body = {
        "instId": instId,
        "tdMode": "cash",
        "side": side,
        "ordType": "market",
        "tgtCcy":"quote_ccy",
        "sz": f"{quote_amount:.8f}"
    }
    with httpx.Client(base_url=OKX_BASE, timeout=20) as c:
        j = json.dumps(body, separators=(",",":"))
        h = _okx_headers(c, "POST", "/api/v5/trade/order", j)
        r = c.post("/api/v5/trade/order", headers=h, content=j)
        return {"status": r.status_code, "json": r.json()}

def _place_order_swap_market(instId:str, sz:float, side:str="buy", tdMode:str="cross")->Dict[str,Any]:
    """以 **張數** 下 **SWAP 市價單**"""
    body = {
        "instId": instId,
        "tdMode": tdMode,         # "cross" 或 "isolated"
        "side": side,
        "ordType": "market",
        "sz": f"{sz}",
        "posSide":"net"
    }
    with httpx.Client(base_url=OKX_BASE, timeout=20) as c:
        j = json.dumps(body, separators=(",",":"))
        h = _okx_headers(c, "POST", "/api/v5/trade/order", j)
        r = c.post("/api/v5/trade/order", headers=h, content=j)
        return {"status": r.status_code, "json": r.json()}

# --- 讀 instrument（拿到 minNotional、ctVal/tick 等） ---
def get_instrument(inst:str, instType:str)->Dict[str,Any]:
    with httpx.Client(base_url=os.getenv("API_BASE", ""), timeout=15) as c:
        # 優先走本服務封裝的 /api/okx/instrument（含 minNotional & ui_hint）
        base = os.getenv("SELF_BASE_URL", "http://127.0.0.1:8000")
        try:
            r = httpx.get(f"{base}/api/okx/instrument", params={"inst":inst,"instType":instType}, timeout=12)
            if r.status_code==200:
                return r.json()
        except Exception:
            pass
    # 後備直打 OKX (只拿必要欄位)
    with httpx.Client(base_url=OKX_BASE, timeout=15) as c:
        r = c.get("/api/v5/public/instruments", params={"instType":instType, "uly":inst if instType in ("SWAP","FUTURES") else None, "instId": inst})
        data = r.json().get("data",[]) or [{}]
        last = c.get("/api/v5/market/ticker", params={"instId": inst}).json().get("data",[{}])[0].get("last","0")
        info = data[0] if data else {}
        return {
            "instId": inst,
            "instType": instType,
            "rules": {
                "minSz": float(info.get("minSz","0") or 0) if "minSz" in info else 0.0,
                "lotSz": float(info.get("lotSz","0") or 0) if "lotSz" in info else 0.0,
                "tickSz": float(info.get("tickSz","0.1") or 0.1),
                "ctVal": float(info.get("ctVal","0") or 0) if "ctVal" in info else 0.0,
                "ctMult": float(info.get("ctMult","1") or 1),
            },
            "price": {"last": float(last or 0)}
        }

# --- 讀風控 ---
def get_risk_limits(user_id:str)->Dict[str,Any]:
    base = os.getenv("SELF_BASE_URL", "http://127.0.0.1:8000")
    try:
        r = httpx.get(f"{base}/api/risk/limits", params={"user_id":user_id}, timeout=8)
        if r.status_code==200:
            return r.json()
    except Exception:
        pass
    return {"max_symbol":0.0,"max_total":0.0,"daily_loss":0.0,"window":"00:00-23:59"}

def _within_window(window_str:str, now_ts:Optional[float]=None)->bool:
    now_ts = now_ts or time.time()
    local = time.localtime(now_ts)
    hhmm = f"{local.tm_hour:02d}:{local.tm_min:02d}"
    try:
        a,b = window_str.split("-")
        return (a <= hhmm <= b) if a<=b else (hhmm>=a or hhmm<=b)
    except Exception:
        return True

# --- 當日 PnL（best-effort） ---
def _get_daily_pnl()->Tuple[float,float]:
    """回傳 (realized_pnl_today, unrealized_pnl_now)。抓不到就回 (0,0)。"""
    realized = 0.0
    unreal   = 0.0
    try:
        with httpx.Client(base_url=OKX_BASE, timeout=20) as c:
            # 取 today 的部分成交（realized 粗估）
            h = _okx_headers(c, "GET", "/api/v5/trade/fills-history")
            r = c.get("/api/v5/trade/fills-history", headers=h, params={"limit":"100"})
            if r.status_code==200:
                for it in r.json().get("data",[]):
                    # OKX 不直接回 realized pnl，這裡以 taker 費用+價差估（保守：不扣正負，記為 0）
                    pass
            # 取未平倉的浮盈虧（unrealized）
            h2 = _okx_headers(c, "GET", "/api/v5/account/positions")
            r2 = c.get("/api/v5/account/positions", headers=h2)
            if r2.status_code==200:
                for p in r2.json().get("data",[]):
                    upl = p.get("upl") or "0"
                    unreal += float(upl)
    except Exception:
        return 0.0, 0.0
    return realized, unreal

# --- 讀 AI 設定 ---
def get_ai_settings(user_id:str)->Dict[str,Any]:
    base = os.getenv("SELF_BASE_URL", "http://127.0.0.1:8000")
    r = httpx.get(f"{base}/api/ai/settings", params={"user_id":user_id}, timeout=8)
    if r.status_code==200:
        rows = r.json().get("rows",{})
        # 可能是字串，嘗試 json 轉 dict
        out={}
        for k,v in rows.items():
            if isinstance(v,str):
                try: out[k]=json.loads(v)
                except: out[k]=v
            else:
                out[k]=v
        return out
    return {}

# --- 主策略：DCA（SPOT: 用 budget 名目；SWAP: 用 sz 張） ---
def run_dca(user_id:str)->Dict[str,Any]:
    ai = get_ai_settings(user_id)
    dca = ai.get("dca") or {}
    symbols = dca.get("symbols") or []
    instType = (dca.get("instType") or "SPOT").upper()
    result = {"ok": False, "orders": [], "reason": ""}

    # 風控/時窗/日內虧損
    rk = get_risk_limits(user_id)
    if not _within_window(rk.get("window","00:00-23:59")):
        result["reason"]="outside_window"
        return result
    realized, unreal = _get_daily_pnl()
    if rk.get("daily_loss",0)>0 and (realized+unreal) <= -abs(float(rk["daily_loss"])):
        result["reason"]="daily_loss_stop"
        return result

    if instType=="SPOT":
        budget = float(dca.get("budget", 0))
        if budget <= 0 or not symbols:
            result["reason"]="missing_budget_or_symbols"
            return result
        per = budget / max(1,len(symbols))
        for s in symbols:
            info = get_instrument(s, "SPOT")
            # 安全下單：若 minNotional 存在，至少覆蓋 minNotional
            minNotional = float(info.get("rules",{}).get("minNotional", 0) or 0)
            quote = max(per, minNotional or 1.0)
            o = _place_order_spot_market_quote(s, quote, side="buy")
            result["orders"].append({"instId":s, "notional":quote, "resp":o})
        result["ok"]=True
        return result

    elif instType in ("SWAP","FUTURES"):
        # SWAP：以「張」下單
        sz = float(dca.get("sz", 0) or 0)
        if sz <= 0 or not symbols:
            result["reason"]="missing_sz_or_symbols"
            return result
        for s in symbols:
            o = _place_order_swap_market(s, sz, side="buy", tdMode=dca.get("tdMode","cross"))
            result["orders"].append({"instId":s, "sz":sz, "resp":o})
        result["ok"]=True
        return result

    result["reason"]="unsupported_instType"
    return result

#（之後可擴：run_breakout/run_grid）
