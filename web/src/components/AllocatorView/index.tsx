import { useEffect } from "react"
import { useAutopilotStore } from "../../store/autopilot"

export function AllocatorView() {
  const { status, load } = useAutopilotStore()

  useEffect(() => {
    load()
  }, [load])

  const orders = status?.last_orders ?? []

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Allocator Snapshot</h3>
        <span className="text-xs text-muted-foreground">Universe size: {status?.universe?.length ?? 0}</span>
      </div>
      <div className="mt-4 space-y-3">
        {orders.length === 0 && <div className="text-sm text-muted-foreground">No orders generated yet.</div>}
        {orders.map((order: any, idx: number) => (
          <div key={idx} className="rounded border border-slate-800 bg-slate-950/50 p-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-white">{order.symbol}</span>
              <span className="text-xs uppercase text-blue-300">{order.status}</span>
            </div>
            <div className="mt-1 text-xs text-muted-foreground">Allocation: ${order.size?.toFixed?.(2) ?? order.size}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
