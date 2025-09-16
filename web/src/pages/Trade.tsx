import { useState } from "react";
import { OrderForm, OrderInput } from "../components/OrderForm";
import { OcoForm, OcoParams } from "../components/OcoForm";
import { fetchBalance, submitAlgoOrder, submitOrder } from "../api/broker";

export default function TradePage() {
  const [lastOrder, setLastOrder] = useState<any>(null);
  const [lastBalance, setLastBalance] = useState<any>(null);
  const [ocoParams, setOcoParams] = useState<OcoParams | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (input: OrderInput) => {
    setLoading(true);
    const payload: Record<string, unknown> = {
      instId: input.instId,
      side: input.side,
      ordType: input.ordType,
      tdMode: "cash",
      notional: input.notional
    };
    if (input.ordType === "limit" && input.px) {
      payload.px = input.px;
    }
    const orderResp = await submitOrder(payload);
    if (ocoParams) {
      await submitAlgoOrder({
        instId: input.instId,
        side: input.side === "buy" ? "sell" : "buy",
        ordType: "oco",
        tpTriggerPx: String(ocoParams.tp_pct),
        slTriggerPx: String(ocoParams.sl_pct),
        sz: "1"
      });
    }
    setLastOrder(orderResp);
    setLoading(false);
  };

  const handleBalance = async () => {
    const resp = await fetchBalance();
    setLastBalance(resp);
  };

  return (
    <div className="grid gap-6 md:grid-cols-[2fr,1fr]">
      <div className="space-y-4">
        <OrderForm onSubmit={handleSubmit} loading={loading} />
        <OcoForm onSubmit={setOcoParams} />
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="flex items-center justify-between text-sm font-semibold text-slate-200">
            <span>最新回應</span>
            <button onClick={handleBalance} className="rounded bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-slate-700">
              重新取得餘額
            </button>
          </div>
          <pre className="mt-3 max-h-64 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {lastOrder ? JSON.stringify(lastOrder, null, 2) : "尚無下單紀錄"}
          </pre>
        </div>
      </div>
      <div className="space-y-4">
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">餘額資訊</div>
          <pre className="mt-3 max-h-64 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {lastBalance ? JSON.stringify(lastBalance, null, 2) : "尚未載入"}
          </pre>
        </div>
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4 text-xs text-slate-400">
          <div className="text-sm font-semibold text-slate-200">OCO 參數</div>
          <pre className="mt-3 rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {ocoParams ? JSON.stringify(ocoParams, null, 2) : "未設定"}
          </pre>
        </div>
      </div>
    </div>
  );
}
