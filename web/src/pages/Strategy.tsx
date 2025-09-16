import { useState } from "react";
import { executeStrategy } from "../api/strategy";
import { AllocatorView } from "../components/AllocatorView";

const STRATEGIES = [
  { id: "dca", label: "DCA" },
  { id: "breakout", label: "Breakout" },
  { id: "grid", label: "Grid" }
];

export default function StrategyPage() {
  const [strategy, setStrategy] = useState("dca");
  const [params, setParams] = useState<Record<string, any>>({ lookback: 200 });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    setLoading(true);
    const resp = await executeStrategy({ strategy, params });
    setResult(resp);
    setLoading(false);
  };

  return (
    <div className="grid gap-6 md:grid-cols-[1fr,1fr]">
      <div className="space-y-4">
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">策略設定</div>
          <div className="mt-3 flex gap-3 text-xs text-slate-300">
            {STRATEGIES.map((item) => (
              <button
                key={item.id}
                onClick={() => setStrategy(item.id)}
                className={`rounded px-3 py-1 ${strategy === item.id ? "bg-sky-500 text-slate-900" : "bg-slate-800"}`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <label className="mt-4 flex flex-col text-xs text-slate-400">
            參數 JSON
            <textarea
              rows={6}
              className="mt-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
              value={JSON.stringify(params, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setParams(parsed);
                } catch (err) {
                  // ignore parse errors while typing
                }
              }}
            />
          </label>
          <button
            onClick={handleExecute}
            disabled={loading}
            className="mt-4 rounded bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? "執行中..." : "執行策略"}
          </button>
        </div>
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">結果</div>
          <pre className="mt-3 max-h-80 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {result ? JSON.stringify(result, null, 2) : "尚未執行"}
          </pre>
        </div>
      </div>
      <div className="space-y-4">
        <AllocatorView allocation={result?.allocation ?? null} />
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4 text-xs text-slate-400">
          <div className="text-sm font-semibold text-slate-200">AI 模型</div>
          <div className="mt-2 text-lg text-sky-400">{result?.tier ?? "--"}</div>
          <div className="mt-1 text-slate-300">成本: {result?.cost ?? "--"}</div>
          <div className="mt-2 text-slate-400">下一次建議: {result?.next_interval_s ? `${Math.round(result.next_interval_s)}s` : "--"}</div>
        </div>
      </div>
    </div>
  );
}
