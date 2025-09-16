import { api, type ApiResponse } from "./client"

export type BacktestResult = {
  strategy: string
  equity: { ts: string; value: number }[]
  kpi: {
    total_return: number
    sharpe: number
    max_drawdown: number
  }
}

export const runBacktest = async (payload: { strategy: string; days: number }) => {
  const res = await api.post("api/backtest/run", { json: payload }).json<ApiResponse<BacktestResult>>()
  return res.data
}
