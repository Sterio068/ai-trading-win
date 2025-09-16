interface AllocatorViewProps {
  allocation: Record<string, any> | null;
}

export function AllocatorView({ allocation }: AllocatorViewProps) {
  if (!allocation) return null;
  const items = allocation.allocations ?? [];
  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-sm font-semibold text-slate-200">資產配置</div>
      <div className="mt-2 grid gap-2 md:grid-cols-3">
        <div className="rounded bg-slate-900/80 p-3 text-xs text-slate-400">
          <div>總資金</div>
          <div className="text-lg text-sky-400">{Number(allocation.total_capital ?? 0).toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-900/80 p-3 text-xs text-slate-400">
          <div>日投資上限</div>
          <div className="text-lg text-sky-400">{Number(allocation.daily_limit ?? 0).toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-900/80 p-3 text-xs text-slate-400">
          <div>單筆上限</div>
          <div className="text-lg text-sky-400">{Number(allocation.single_trade_limit ?? 0).toFixed(2)}</div>
        </div>
      </div>
      <div className="mt-4 space-y-2">
        {items.map((item: any) => (
          <div key={item.instId} className="flex items-center justify-between rounded bg-slate-900/70 px-3 py-2 text-xs text-slate-300">
            <span>{item.instId}</span>
            <span>{(item.weight * 100).toFixed(1)}% / {Number(item.notional).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
