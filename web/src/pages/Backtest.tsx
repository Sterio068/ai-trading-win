import { useState } from "react"
import { runBacktest, type BacktestResult } from "../api/backtest"
import { BacktestChart } from "../shared/BacktestChart"

export default function Backtest() {
  const [strategy, setStrategy] = useState("dca")
  const [days, setDays] = useState(30)
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    const data = await runBacktest({ strategy, days })
    setResult(data)
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Backtest Lab</h1>
      <div className="flex flex-wrap gap-3">
        <select
          className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
        >
          <option value="dca">DCA</option>
          <option value="breakout">Breakout</option>
          <option value="grid">Grid</option>
        </select>
        <input
          type="number"
          className="w-24 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        />
        <button className="rounded bg-blue-500 px-3 py-2 text-sm" onClick={handleRun} disabled={loading}>
          {loading ? "Running..." : "Run"}
        </button>
      </div>
      <BacktestChart data={result} />
      {result && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-sm">
          <div>Total return: {(result.kpi.total_return * 100).toFixed(2)}%</div>
          <div>Sharpe: {result.kpi.sharpe.toFixed(2)}</div>
          <div>Max drawdown: {(result.kpi.max_drawdown * 100).toFixed(2)}%</div>
        </div>
      )}
    </div>
  )
}
