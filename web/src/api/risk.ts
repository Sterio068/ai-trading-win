import { api, type ApiResponse } from "./client"

export type RiskStatus = {
  config: {
    cooldown_seconds: number
    max_exposure_pct: number
    daily_loss_limit: number
    max_drawdown_pct: number
  }
  daily_loss: number
  exposure: Record<string, number>
  drawdown: number
  current_equity: number
}

export const fetchRisk = async () => {
  const res = await api.get("api/risk/status").json<ApiResponse<RiskStatus>>()
  return res.data
}

export const updateRisk = async (payload: Partial<RiskStatus["config"]>) => {
  const res = await api.post("api/risk/config", { json: payload }).json<ApiResponse<RiskStatus>>()
  return res.data
}

export const resetRisk = async () => {
  const res = await api.post("api/risk/reset").json<ApiResponse<RiskStatus>>()
  return res.data
}
