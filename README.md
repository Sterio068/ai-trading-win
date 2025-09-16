# AI 全自動量化交易系統

本專案提供一套可於 Windows 本機啟動的 AI 自動量化交易系統，涵蓋 FastAPI 後端與 Vite + React 前端。系統整合 OKX 交易所、AI 決策模組、風控與自動駕駛 (Autopilot) 等功能。

## 專案結構

```
├── backend                # FastAPI 後端
├── web                    # Vite + React 前端
├── storage                # JSON 狀態檔案
├── exports                # CSV 審計輸出
└── README.md
```

## 環境需求
- Python 3.11+
- Node.js 18+
- npm 9+

## 後端啟動

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> 若需使用 Windows PowerShell 啟動虛擬環境請改用 `.venv\\Scripts\\Activate.ps1`。

## 前端啟動

```bash
cd web
npm install
npm run dev
```

## 基礎驗收指令

後端啟動後可執行以下指令確認功能：

```bash
curl -s http://127.0.0.1:8000/healthz
curl -s http://127.0.0.1:8000/api/env
curl -s -X POST http://127.0.0.1:8000/api/env/switch-mode -H "content-type: application/json" -d '{"mode":"paper"}'
curl -s http://127.0.0.1:8000/api/broker/okx/balance
curl -s -X POST http://127.0.0.1:8000/api/backtest/run -H "content-type: application/json" -d '{"instId":"BTC-USDT","exchange":"okx","strategy":"dca","params":{"lookback":200,"every_n":5,"budget":20}}'
curl -s -X POST http://127.0.0.1:8000/api/strategy/autopilot/start -H "content-type: application/json" -d '{"base_interval_s": 60}'
curl -s -X POST http://127.0.0.1:8000/api/strategy/autopilot/stop
curl -s http://127.0.0.1:8000/ops/metrics | head
```

## 設定檔案

- `.env`：保存在專案根目錄，由後端 API 寫入與遮蔽顯示。
- `storage/*.json`：儲存風控狀態、AI 成本、Autopilot 狀態等。
- `exports/*.csv`：匯出審計紀錄。

## 主要功能概述
- OKX Broker 介面，支援紙本/實盤憑證切換
- AI 決策中樞，三層模型自動選型與成本控管
- 風險控管：日損、曝險、冷卻、最大回撤
- 回測引擎與 KPI 指標計算
- Autopilot 自動駕駛排程，依 AI 頻率策略自調整
- 前端設定、交易、策略、風控、回測、情緒與 Autopilot 監控頁面

## 注意事項
- 無外網情境下，OKX API 會回傳模擬資料且不會實際下單。
- Sentry 可選擇性設定 `SENTRY_DSN` 後啟用。
- 若需要 SQLite 儲存可擴充 `storage` 相關模組，本專案預設使用 JSON。
