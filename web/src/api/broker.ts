import { api, type ApiResponse } from "./client"

export const fetchBalance = async () => {
  const res = await api.get("api/broker/okx/balance").json<ApiResponse<any>>()
  return res.data
}

export const submitOrder = async (payload: Record<string, any>) => {
  const res = await api.post("api/broker/okx/order", { json: payload }).json<ApiResponse<any>>()
  return res.data
}

export const simulateOrder = async (payload: Record<string, any>) => {
  const res = await api
    .post("api/broker/okx/simulate", { json: payload })
    .json<ApiResponse<any>>()
  return res.data
}
