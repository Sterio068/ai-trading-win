import { api, unwrap } from "./client";

export type EnvValues = Record<string, string>;

export async function fetchEnv() {
  return unwrap<{ values: EnvValues }>(api.get("api/env").json());
}

export async function saveEnv(values: EnvValues, updatedBy?: string) {
  return unwrap<{ diff: Record<string, { old: string; new: string }> }>(
    api.post("api/env", { json: { values, updated_by: updatedBy } }).json()
  );
}

export async function switchMode(mode: "paper" | "real") {
  return unwrap<{ diff: Record<string, { old: string; new: string }> }>(
    api.post("api/env/switch-mode", { json: { mode } }).json()
  );
}
