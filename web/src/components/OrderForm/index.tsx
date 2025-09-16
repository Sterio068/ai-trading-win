import { useState } from "react"
import { simulateOrder, submitOrder } from "../../api/broker"

const ORDER_TYPES = [
  { label: "Market", value: "market" },
  { label: "Limit", value: "limit" },
]

export function OrderForm() {
  const [form, setForm] = useState({
    instId: "BTC-USDT",
    side: "buy",
    ordType: "market",
    px: "",
    sz: "0.01",
  })
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async (simulate = false) => {
    setLoading(true)
    const payload: any = {
      instId: form.instId,
      side: form.side,
      ordType: form.ordType,
      tdMode: "cash",
      sz: form.sz,
    }
    if (form.ordType === "limit") {
      payload.px = form.px
    }
    const result = simulate ? await simulateOrder(payload) : await submitOrder(payload)
    setResponse(result)
    setLoading(false)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <h3 className="text-lg font-semibold">Order Ticket</h3>
      <div className="mt-3 grid gap-3">
        <label className="text-xs uppercase text-slate-400">
          Instrument
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
            value={form.instId}
            onChange={(e) => handleChange("instId", e.target.value)}
          />
        </label>
        <div className="flex gap-3">
          <label className="flex-1 text-xs uppercase text-slate-400">
            Side
            <select
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
              value={form.side}
              onChange={(e) => handleChange("side", e.target.value)}
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </label>
          <label className="flex-1 text-xs uppercase text-slate-400">
            Type
            <select
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
              value={form.ordType}
              onChange={(e) => handleChange("ordType", e.target.value)}
            >
              {ORDER_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        {form.ordType === "limit" && (
          <label className="text-xs uppercase text-slate-400">
            Price
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
              value={form.px}
              onChange={(e) => handleChange("px", e.target.value)}
            />
          </label>
        )}
        <label className="text-xs uppercase text-slate-400">
          Size
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
            value={form.sz}
            onChange={(e) => handleChange("sz", e.target.value)}
          />
        </label>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          className="rounded-lg bg-blue-500 px-3 py-2 text-sm font-semibold text-white"
          onClick={() => handleSubmit(false)}
          disabled={loading}
        >
          {loading ? "Submitting" : "Submit"}
        </button>
        <button
          className="rounded-lg border border-slate-700 px-3 py-2 text-sm"
          onClick={() => handleSubmit(true)}
          disabled={loading}
        >
          Simulate
        </button>
      </div>
      {response && (
        <pre className="mt-4 max-h-48 overflow-y-auto rounded bg-slate-950/60 p-3 text-xs text-emerald-200">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  )
}
