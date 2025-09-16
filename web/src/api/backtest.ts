import { api, unwrap } from "./client";

export async function runBacktest(payload: Record<string, unknown>) {
  return unwrap(api.post("api/backtest/run", { json: payload }).json());
}
