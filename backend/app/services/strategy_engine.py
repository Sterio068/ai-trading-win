import re, json, math, os
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.app.svc import db as svc_db
from sqlalchemy import select, insert
from backend.app.services.okx_core import get_instrument, get_ticker, place_spot_market_quote, place_swap_market, est_min_notional
from backend.app.services.ai_openai import plan as ai_plan

def in_window(win:str)->bool:
    try:
        now = datetime.utcnow()
        cur = now.hour*60+now.minute
        a,b = win.split("-"); h1,m1 = [int(x) for x in a.split(":")]; h2,m2=[int(x) for x in b.split(":")]
        s,e = h1*60+m1, h2*60+m2
        return (s<=e and s<=cur<=e) or (s>e and (cur>=s or cur<=e))
    except:
        return True

async def get_limits(user_id:str)->Dict[str,Any]:
    row = await svc_db.db.fetch_one(select(svc_db.risk_limits).where(svc_db.risk_limits.c.user_id==user_id))
    if not row:
        return {"max_symbol":0,"max_total":0,"daily_loss":0,"window":"00:00-23:59"}
    return {"max_symbol":float(row["max_symbol"]), "max_total":float(row["max_total"]),
            "daily_loss":float(row["daily_loss"]), "window":row["window"]}

def pnl_guard(user_id:str)->bool:
    # 這裡可對接 OKX /account/positions 與 /trade/fills 計算日內 PnL。單機版先回 True（不擋）。
    return True

async def run_dca(settings:Dict[str,Any])->Dict[str,Any]:
    user_id = settings.get("_user_id")
    dca = settings.get("dca") or {}
    instType = (dca.get("instType") or "SPOT").upper()
    syms = dca.get("symbols") or []
    budget = float(dca.get("budget") or settings.get("prefs",{}).get("budget") or 0)
    swap_cfg = settings.get("dca_swap") or {}
    swap_sz = float(dca.get("sz") or swap_cfg.get("sz") or 0)

    limits = await get_limits(user_id or "")
    if not in_window(limits["window"]): 
        return {"ok":False,"reason":"outside_window"}
    if not pnl_guard(user_id or ""):
        return {"ok":False,"reason":"pnl_guard"}

    if not syms:
        return {"ok":False,"reason":"no_symbols"}

    results=[]
    for instId in syms:
        # 規則/現價
        info,minSz,lotSz,tickSz,ctVal,ctMult = get_instrument(instId, instType)
        last = get_ticker(instId)
        minNotional = est_min_notional(instType, minSz, last, ctVal, ctMult)

        # 構造 AI 決策 context（會受風控與最小名目約束）
        ctx = {
            "instId":instId,"instType":instType,
            "price":{"last":last},"rules":{"minSz":minSz,"lotSz":lotSz,"tickSz":tickSz,"ctVal":ctVal,"ctMult":ctMult,"minNotional":minNotional},
            "risk":limits,"sentiment":0.0,"vol":0.0,
            "budget":budget if instType=="SPOT" else swap_sz,
            "budget_cap": max(minNotional, budget if instType=="SPOT" else swap_sz),
        }
        decision = ai_plan(ctx)
        action = (decision.get("action") or "hold").lower()

        try:
            if instType=="SPOT":
                use_budget = max(budget, minNotional) if action=="buy" else 0
                if action!="buy" or use_budget<=0:
                    results.append({"instId":instId,"ok":True,"skip":True,"reason":decision.get("reason")})
                    continue
                r = place_spot_market_quote(instId, use_budget)
                results.append({"instId":instId,"ok":True,"resp":r})
            else:
                use_sz = max(swap_sz, minSz) if action=="buy" else 0
                if action!="buy" or use_sz<=0:
                    results.append({"instId":instId,"ok":True,"skip":True,"reason":decision.get("reason")})
                    continue
                r = place_swap_market(instId, use_sz)
                results.append({"instId":instId,"ok":True,"resp":r})
        except Exception as e:
            results.append({"instId":instId,"ok":False,"error":str(e),"decision":decision})

    any_ok = any(x.get("ok") and not x.get("skip") for x in results)
    return {"ok": any_ok, "results":results}
