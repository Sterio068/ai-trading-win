import { useState } from "react";

export interface OrderInput {
  instId: string;
  side: "buy" | "sell";
  ordType: "market" | "limit";
  notional: number;
  px?: number;
}

interface OrderFormProps {
  onSubmit: (input: OrderInput) => Promise<void>;
  loading?: boolean;
}

export function OrderForm({ onSubmit, loading }: OrderFormProps) {
  const [form, setForm] = useState<OrderInput>({
    instId: "BTC-USDT",
    side: "buy",
    ordType: "market",
    notional: 10
  });

  const handleChange = (key: keyof OrderInput, value: string) => {
    setForm((prev) => ({ ...prev, [key]: key === "notional" || key === "px" ? Number(value) : value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-sm font-semibold text-slate-200">下單</div>
      <div className="grid gap-2 md:grid-cols-2">
        <label className="flex flex-col text-xs text-slate-400">
          交易對
          <input
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.instId}
            onChange={(e) => handleChange("instId", e.target.value)}
          />
        </label>
        <label className="flex flex-col text-xs text-slate-400">
          價格類型
          <select
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.ordType}
            onChange={(e) => handleChange("ordType", e.target.value)}
          >
            <option value="market">市價</option>
            <option value="limit">限價</option>
          </select>
        </label>
        <label className="flex flex-col text-xs text-slate-400">
          方向
          <select
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.side}
            onChange={(e) => handleChange("side", e.target.value)}
          >
            <option value="buy">買入</option>
            <option value="sell">賣出</option>
          </select>
        </label>
        <label className="flex flex-col text-xs text-slate-400">
          數量（Notional）
          <input
            type="number"
            step="0.01"
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.notional}
            onChange={(e) => handleChange("notional", e.target.value)}
          />
        </label>
        {form.ordType === "limit" && (
          <label className="flex flex-col text-xs text-slate-400 md:col-span-2">
            價格
            <input
              type="number"
              step="0.01"
              className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
              value={form.px ?? ""}
              onChange={(e) => handleChange("px", e.target.value)}
            />
          </label>
        )}
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-sky-500 py-2 text-sm font-semibold text-slate-900 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-700"
      >
        {loading ? "送出中..." : "送出訂單"}
      </button>
    </form>
  );
}
