import { api, type ApiResponse } from "./client"

export type EnvSettings = Record<string, string>

export const fetchEnv = async () => {
  const res = await api.get("api/env").json<ApiResponse<EnvSettings>>()
  return res.data
}

export const updateEnv = async (payload: Partial<EnvSettings>) => {
  const res = await api.post("api/env", { json: payload }).json<ApiResponse<EnvSettings>>()
  return res.data
}

export const switchMode = async (mode: "PAPER" | "REAL") => {
  const res = await api
    .post("api/env/switch-mode", { json: { mode } })
    .json<ApiResponse<{ mode: string }>>()
  return res.data
}
