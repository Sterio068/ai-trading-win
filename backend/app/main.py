import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, Response, FileResponse
from starlette.staticfiles import StaticFiles
from prometheus_client import REGISTRY, CONTENT_TYPE_LATEST, generate_latest
from backend.app.svc import db as svc_db
from backend.app.routers import all_routes
from backend.app.routers import strategy
from backend.app.middlewares import install_middlewares

app = FastAPI(title="AI Trading (Windows One-Click)")
app.include_router(strategy.router)
install_middlewares(app)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx, os, json

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def _start_scheduler():
    # 啟動排程器
    if not scheduler.running:
        scheduler.start()
    # 從 DB 把所有有 cron 的設定掃一遍（僅示範 dca）
    base = os.getenv("SELF_BASE_URL", "http://127.0.0.1:8000")
    # 這裡示範單帳號；正式可掃 ai_settings 使用者清單
    users = [os.getenv("DEFAULT_USER","sterio068@mail.com")]
    for uid in users:
        try:
            r = httpx.get(f"{base}/api/ai/settings", params={"user_id":uid}, timeout=8)
            if r.status_code==200:
                rows = r.json().get("rows",{})
                dca = rows.get("dca")
                if isinstance(dca, str):
                    try: dca=json.loads(dca)
                    except: dca=None
                if isinstance(dca, dict) and dca.get("cron"):
                    cron = dca["cron"]
                    job_id = f"dca::{uid}"
                    if scheduler.get_job(job_id):
                        scheduler.remove_job(job_id)
                    # 用簡易 cron 表達式（分 時 日 月 週）
                    scheduler.add_job(
                        lambda: httpx.post(f"{base}/api/strategy/run", json={"kind":"dca","user_id":uid}, timeout=30),
                        trigger="cron",
                        id=job_id,
                        **_parse_cron(cron)
                    )
        except Exception:
            pass

def _parse_cron(cron_text:str):
    # "*/15 * * * *" → {'minute': '*/15'}
    fields = (cron_text or "* * * * *").split()
    out={}
    if len(fields)>=1: out["minute"]=fields[0]
    if len(fields)>=2: out["hour"]=fields[1]
    if len(fields)>=3: out["day"]=fields[2]
    if len(fields)>=4: out["month"]=fields[3]
    if len(fields)>=5: out["day_of_week"]=fields[4]
    return out

CORS = os.getenv("CORS_ORIGINS","*")
origins = [o.strip() for o in CORS.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins else ["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.on_event("startup")
async def on_start():
    from backend.app.svc.db import init_schema, init_pool
    init_schema()
    await init_pool()

@app.on_event("shutdown")
async def on_shutdown():
    from backend.app.svc.db import close_pool
    await close_pool()

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz(): return "ok"

@app.get("/readyz")
async def readyz(): return {"ready": True}

@app.get("/metrics")
async def metrics(): return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# 靜態 UI
app.mount("/ui", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..","..","ui"), html=True), name="ui")
@app.get("/")
async def root(): return FileResponse(os.path.join(os.path.dirname(__file__), "..","..","ui","index.html"))

# 路由
app.include_router(all_routes.router)
