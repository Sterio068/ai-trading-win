import ky from "ky";

type ApiMeta = {
  request_id: string;
  ts: number;
};

type ApiSuccess<T> = {
  ok: true;
  data: T;
  meta: ApiMeta;
};

type ApiFailure = {
  ok: false;
  error: {
    code: string;
    message: string;
    hint?: string;
  };
  meta: ApiMeta;
};

export type ApiEnvelope<T> = ApiSuccess<T> | ApiFailure;

const prefixUrl = import.meta.env.VITE_API ?? "http://127.0.0.1:8000";

export const api = ky.create({
  prefixUrl,
  headers: {
    "content-type": "application/json"
  }
});

export async function unwrap<T>(promise: Promise<ApiEnvelope<T>>): Promise<T> {
  const json = await promise;
  if (!json.ok) {
    const error = json.error;
    throw new Error(`${error.code}: ${error.message}${error.hint ? ` (${error.hint})` : ""}`);
  }
  return json.data;
}

export function getApiBase(): string {
  return prefixUrl;
}
