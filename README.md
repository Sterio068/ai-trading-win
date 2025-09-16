# AI 自動量化交易系統

本專案提供一個可立即啟動的 AI 自動量化交易系統，包含 FastAPI 後端與 Vite React 前端。

## 專案結構
```
├── backend            # FastAPI 後端
├── web                # Vite React 前端
├── storage            # JSON 儲存
└── exports            # 匯出資料
```

## 快速開始

### 1. 後端啟動
```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\activate
# 或 Unix-like
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. 前端啟動
```bash
cd web
npm install
npm run dev
```

### 3. 驗收腳本
啟動後可使用以下指令驗收：
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/api/env
curl -X POST http://localhost:8000/api/env/switch-mode -H "Content-Type: application/json" -d '{"mode":"REAL"}'
curl http://localhost:8000/api/broker/okx/balance
curl -X POST http://localhost:8000/api/backtest/run -H "Content-Type: application/json" -d '{"strategy":"dca","days":7}'
curl -X POST http://localhost:8000/api/strategy/autopilot/start
curl -X POST http://localhost:8000/api/strategy/autopilot/stop
curl http://localhost:8000/ops/metrics
```

## 其他說明
- 所有設定將寫入專案根目錄的 `.env`。
- 若要使用 Sentry，請在 `.env` 設定 `SENTRY_DSN`。
- SQLite 介面預留但預設關閉。
