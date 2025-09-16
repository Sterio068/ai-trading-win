import { api, type ApiResponse } from "./client"

export type StrategyItem = {
  name: string
  description: string
  complexity: number
}

export const fetchStrategies = async () => {
  const res = await api.get("api/strategy/list").json<ApiResponse<StrategyItem[]>>()
  return res.data
}

export const executeStrategy = async (strategy: string, universe?: string[]) => {
  const res = await api
    .post("api/strategy/execute", { json: { strategy, universe } })
    .json<ApiResponse<any>>()
  return res.data
}

export const startAutopilot = async (interval?: number) => {
  const res = await api
    .post("api/strategy/autopilot/start", { json: interval ? { interval } : {} })
    .json<ApiResponse<any>>()
  return res.data
}

export const stopAutopilot = async () => {
  const res = await api.post("api/strategy/autopilot/stop").json<ApiResponse<any>>()
  return res.data
}

export const autopilotStatus = async () => {
  const res = await api.get("api/strategy/autopilot/status").json<ApiResponse<any>>()
  return res.data
}
