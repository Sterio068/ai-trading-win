import { useState } from "react";
import { useAutopilotStore } from "../store/autopilot";

export default function HomePage() {
  const { state, start, stop, loading, error } = useAutopilotStore();
  const [instId, setInstId] = useState("");
  const [interval, setInterval] = useState(120);

  const running = Boolean(state?.running);
  const costToday = state?.cost_today as { remaining?: number; limit?: number } | undefined;

  return (
    <div className="space-y-6">
      <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
        <div className="text-lg font-semibold text-slate-100">Autopilot 狀態</div>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="rounded bg-slate-900/80 p-4 text-xs text-slate-400">
            <div className="text-slate-200">運行中</div>
            <div className={`text-2xl ${running ? "text-emerald-400" : "text-slate-500"}`}>
              {running ? "ON" : "OFF"}
            </div>
          </div>
          <div className="rounded bg-slate-900/80 p-4 text-xs text-slate-400">
            <div className="text-slate-200">下一次呼叫</div>
            <div className="text-2xl text-sky-400">{state?.next_interval_s ? `${Math.round(Number(state.next_interval_s))}s` : "--"}</div>
          </div>
          <div className="rounded bg-slate-900/80 p-4 text-xs text-slate-400">
            <div className="text-slate-200">今日成本</div>
            <div className="text-2xl text-amber-300">
              {costToday ? `${(costToday.limit ?? 0 - (costToday.remaining ?? 0)).toFixed(3)} / ${(costToday.limit ?? 0).toFixed(2)}` : "--"}
            </div>
          </div>
        </div>
        <div className="mt-6 flex flex-col gap-3 md:flex-row">
          <input
            className="flex-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
            placeholder="instId (可空)"
            value={instId}
            onChange={(e) => setInstId(e.target.value)}
          />
          <input
            type="number"
            className="w-40 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
            value={interval}
            onChange={(e) => setInterval(Number(e.target.value))}
          />
          <button
            onClick={() => start({ instId: instId || undefined, base_interval_s: interval })}
            disabled={loading}
            className="rounded bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400 disabled:opacity-50"
          >
            啟動 Autopilot
          </button>
          <button
            onClick={() => stop()}
            disabled={loading || !running}
            className="rounded bg-rose-500 px-4 py-2 text-sm font-semibold text-slate-50 hover:bg-rose-400 disabled:opacity-50"
          >
            停止
          </button>
        </div>
        {error && <div className="mt-2 text-sm text-rose-400">{error}</div>}
      </div>
      <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
        <div className="text-sm font-semibold text-slate-200">最新決策紀錄</div>
        <pre className="mt-3 max-h-64 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
          {JSON.stringify(state?.last_result ?? {}, null, 2)}
        </pre>
      </div>
    </div>
  );
}
