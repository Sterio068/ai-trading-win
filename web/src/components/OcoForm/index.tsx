import { useState } from "react"
import { simulateOrder } from "../../api/broker"

export function OcoForm() {
  const [form, setForm] = useState({
    instId: "ETH-USDT",
    takeProfit: "2200",
    stopLoss: "1800",
    size: "0.05",
  })
  const [response, setResponse] = useState<any>(null)

  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async () => {
    const tp = await simulateOrder({
      instId: form.instId,
      side: "sell",
      ordType: "limit",
      px: form.takeProfit,
      sz: form.size,
    })
    const sl = await simulateOrder({
      instId: form.instId,
      side: "sell",
      ordType: "stop",
      px: form.stopLoss,
      sz: form.size,
    })
    setResponse({ takeProfit: tp, stopLoss: sl })
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <h3 className="text-lg font-semibold">OCO Simulator</h3>
      <div className="mt-3 grid gap-3">
        <label className="text-xs uppercase text-slate-400">
          Instrument
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
            value={form.instId}
            onChange={(e) => handleChange("instId", e.target.value)}
          />
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="text-xs uppercase text-slate-400">
            Take Profit
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
              value={form.takeProfit}
              onChange={(e) => handleChange("takeProfit", e.target.value)}
            />
          </label>
          <label className="text-xs uppercase text-slate-400">
            Stop Loss
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
              value={form.stopLoss}
              onChange={(e) => handleChange("stopLoss", e.target.value)}
            />
          </label>
        </div>
        <label className="text-xs uppercase text-slate-400">
          Size
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
            value={form.size}
            onChange={(e) => handleChange("size", e.target.value)}
          />
        </label>
      </div>
      <button className="mt-4 rounded-lg bg-slate-800 px-3 py-2 text-sm" onClick={handleSubmit}>
        Simulate OCO
      </button>
      {response && (
        <pre className="mt-4 max-h-48 overflow-y-auto rounded bg-slate-950/60 p-3 text-xs text-emerald-200">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  )
}
