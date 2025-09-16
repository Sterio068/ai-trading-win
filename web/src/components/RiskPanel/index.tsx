interface RiskPanelProps {
  state: Record<string, any> | null;
}

export function RiskPanel({ state }: RiskPanelProps) {
  if (!state) {
    return <div className="rounded border border-slate-800 bg-slate-900/50 p-4 text-sm text-slate-400">尚未載入風控資料</div>;
  }
  const exposures = state.symbol_exposure || {};
  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-sm font-semibold text-slate-200">風控狀態</div>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <div className="rounded bg-slate-900/80 p-3 text-xs text-slate-400">
          <div className="text-slate-200">Realized PnL</div>
          <div className="text-lg text-emerald-400">{Number(state.realized_pnl ?? 0).toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-900/80 p-3 text-xs text-slate-400">
          <div className="text-slate-200">Equity Peak</div>
          <div className="text-lg text-sky-400">{Number(state.equity_peak ?? 0).toFixed(2)}</div>
        </div>
      </div>
      <div className="mt-4">
        <div className="text-xs font-semibold text-slate-300">曝險</div>
        <div className="mt-2 space-y-1 text-xs">
          {Object.keys(exposures).length === 0 && <div className="text-slate-500">目前無部位</div>}
          {Object.entries(exposures).map(([symbol, value]) => (
            <div key={symbol} className="flex items-center justify-between rounded bg-slate-900/80 px-3 py-2">
              <span className="text-slate-300">{symbol}</span>
              <span className="text-slate-200">{Number(value).toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
