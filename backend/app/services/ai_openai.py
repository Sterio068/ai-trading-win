import os, json, math
from typing import Any, Dict, List

OPEN = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL_GPT5","gpt-5")

def _offline_plan(context:Dict[str,Any])->Dict[str,Any]:
    # 簡單策略：若 sentiment > 0.6 則 buy；<0.4 則 sell；否則 hold
    sent = float(context.get("sentiment",0))
    act = "hold"
    if sent>0.6: act="buy"
    elif sent<0.4: act="sell"
    budget = float(context.get("budget",0))
    est = {"action":act,"budget":min(budget, context.get("budget_cap",budget)), "reason":"offline heuristic"}
    return est

def plan(context:Dict[str,Any])->Dict[str,Any]:
    """
    context = {
      "instId","instType","price":{"last":...},"rules":{"minSz","tickSz","minNotional","ctVal","ctMult"},
      "risk":{"max_symbol","max_total","daily_loss","window"},
      "sentiment":0~1,"vol":0~1,"budget":float,"budget_cap":float
    }
    """
    if not OPEN:
        return _offline_plan(context)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPEN)
        sys = "你是量化交易助理。請輸出 JSON：{action: buy|sell|hold, px: number|null, size_or_budget: number, reason: string}，不得輸出其他內容。"
        usr = f"市況: {json.dumps(context, ensure_ascii=False)}"
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"system","content":sys},{"role":"user","content":usr}],
            temperature=0.2,
        )
        txt = resp.choices[0].message.content.strip()
        # 嘗試擷取 JSON
        import re, json
        m = re.search(r"\{.*\}", txt, re.S)
        js = json.loads(m.group(0)) if m else {}
        action = js.get("action","hold")
        size_or_budget = float(js.get("size_or_budget", context.get("budget",0)))
        return {"action":action, "budget":size_or_budget, "px": js.get("px"), "reason": js.get("reason","model")}
    except Exception as e:
        return {"action":"hold","budget":0,"reason":f"openai_error:{e}"}
