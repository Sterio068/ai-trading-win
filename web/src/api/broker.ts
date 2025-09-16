import { api, unwrap } from "./client";

export async function fetchBalance() {
  return unwrap(api.get("api/broker/okx/balance").json());
}

export async function submitOrder(payload: Record<string, unknown>) {
  return unwrap(api.post("api/broker/okx/order", { json: payload }).json());
}

export async function submitAlgoOrder(payload: Record<string, unknown>) {
  return unwrap(api.post("api/broker/okx/order-algo", { json: payload }).json());
}

export async function fetchOpenOrders(instId: string) {
  return unwrap(api.get("api/broker/okx/open-orders", { searchParams: { instId } }).json());
}

export async function fetchFills(instId: string) {
  return unwrap(
    api
      .get("api/broker/okx/fills-history", { searchParams: { instId } })
      .json()
  );
}
