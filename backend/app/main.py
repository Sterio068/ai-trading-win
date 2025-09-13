import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, Response, FileResponse
from starlette.staticfiles import StaticFiles
from prometheus_client import REGISTRY, CONTENT_TYPE_LATEST, generate_latest
from backend.app.svc import db as svc_db
from backend.app.routers import all_routes

app = FastAPI(title="AI Trading (Windows One-Click)")

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
