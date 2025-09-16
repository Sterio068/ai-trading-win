import { useState } from "react";
import { runBacktest } from "../api/backtest";
import { BacktestChart } from "../shared/BacktestChart";

export default function BacktestPage() {
  const [instId, setInstId] = useState("BTC-USDT");
  const [strategy, setStrategy] = useState("dca");
  const [params, setParams] = useState("{\n  \"lookback\": 200,\n  \"every_n\": 5,\n  \"budget\": 20\n}");
  const [equity, setEquity] = useState<number[]>([]);
  const [stats, setStats] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    const parsed = JSON.parse(params || "{}");
    const resp = await runBacktest({ instId, exchange: "okx", strategy, params: parsed });
    setEquity(resp.equity ?? []);
    setStats(resp.stats ?? null);
    setLoading(false);
  };

  const downloadCsv = () => {
    const rows = equity.map((value, index) => `${index},${value}`);
    const blob = new Blob(["index,equity\n" + rows.join("\n")], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `backtest-${instId}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="space-y-6">
      <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="flex flex-col text-xs text-slate-400">
            instId
            <input
              className="mt-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
              value={instId}
              onChange={(e) => setInstId(e.target.value)}
            />
          </label>
          <label className="flex flex-col text-xs text-slate-400">
            策略
            <select
              className="mt-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
            >
              <option value="dca">DCA</option>
              <option value="breakout">Breakout</option>
              <option value="grid">Grid</option>
            </select>
          </label>
          <button
            onClick={handleRun}
            disabled={loading}
            className="mt-6 rounded bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? "執行中..." : "開始回測"}
          </button>
        </div>
        <label className="mt-4 flex flex-col text-xs text-slate-400">
          參數 JSON
          <textarea
            rows={6}
            className="mt-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
            value={params}
            onChange={(e) => setParams(e.target.value)}
          />
        </label>
      </div>
      {equity.length > 0 && (
        <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between text-sm font-semibold text-slate-200">
            <span>Equity Curve</span>
            <button onClick={downloadCsv} className="rounded bg-slate-800 px-3 py-1 text-xs hover:bg-slate-700">
              下載 CSV
            </button>
          </div>
          <BacktestChart data={equity} />
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {stats &&
              Object.entries(stats).map(([key, value]) => (
                <div key={key} className="rounded bg-slate-900/80 p-3 text-xs text-slate-300">
                  <div className="uppercase tracking-wide text-slate-400">{key}</div>
                  <div className="text-lg text-sky-400">{String(value)}</div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
