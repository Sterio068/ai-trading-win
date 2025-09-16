import { api, unwrap } from "./client";

export async function executeStrategy(payload: Record<string, unknown>) {
  return unwrap(api.post("api/strategy/execute", { json: payload }).json());
}

export async function startAutopilot(payload: { instId?: string; base_interval_s?: number }) {
  return unwrap(api.post("api/strategy/autopilot/start", { json: payload }).json());
}

export async function stopAutopilot() {
  return unwrap(api.post("api/strategy/autopilot/stop").json());
}
