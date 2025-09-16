import { api, unwrap } from "./client";

export async function fetchRiskConfig() {
  return unwrap<Record<string, unknown>>(api.get("api/risk/config").json());
}

export async function fetchRiskState() {
  return unwrap(api.get("api/risk/state").json());
}

export async function updateRiskConfig(config: Record<string, unknown>, updatedBy?: string) {
  return unwrap(
    api.post("api/risk/config", { json: { config, updated_by: updatedBy } }).json()
  );
}

export async function fetchRiskVersion() {
  return unwrap(api.get("api/risk/version").json());
}
