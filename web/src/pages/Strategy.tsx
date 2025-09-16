import { useEffect, useState } from "react"
import { executeStrategy, fetchStrategies } from "../api/strategy"
import { useAutopilotStore } from "../store/autopilot"
import { AllocatorView } from "../components/AllocatorView"

export default function Strategy() {
  const [strategies, setStrategies] = useState<any[]>([])
  const [lastDecision, setLastDecision] = useState<any>(null)
  const { start, stop, status, load } = useAutopilotStore()

  useEffect(() => {
    const loadStrategies = async () => {
      setStrategies(await fetchStrategies())
      await load()
    }
    loadStrategies()
  }, [load])

  const runStrategy = async (name: string) => {
    const result = await executeStrategy(name)
    setLastDecision(result)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Strategy Center</h1>
          <p className="text-sm text-muted-foreground">Manage discretionary executions and Autopilot scheduling.</p>
        </div>
        <div className="flex gap-2">
          <button className="rounded bg-blue-500 px-3 py-2 text-sm font-semibold" onClick={() => start()}>
            Start Autopilot
          </button>
          <button className="rounded border border-slate-700 px-3 py-2 text-sm" onClick={() => stop()}>
            Stop
          </button>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {strategies.map((strategy) => (
          <div key={strategy.name} className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">{strategy.name.toUpperCase()}</h3>
                <p className="text-xs text-muted-foreground">{strategy.description}</p>
              </div>
              <button className="rounded bg-slate-800 px-3 py-1 text-sm" onClick={() => runStrategy(strategy.name)}>
                Execute
              </button>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">Complexity: {strategy.complexity}</div>
          </div>
        ))}
      </div>
      <AllocatorView />
      {lastDecision && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h3 className="text-lg font-semibold">Last Manual Decision</h3>
          <pre className="mt-3 max-h-80 overflow-y-auto rounded bg-slate-950/60 p-3 text-xs text-emerald-200">
            {JSON.stringify(lastDecision, null, 2)}
          </pre>
        </div>
      )}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-sm">
        <div>Autopilot active: {status?.active ? "Yes" : "No"}</div>
        <div>Next decision: {status?.next_run ?? "--"}</div>
        <div>Last model: {status?.last_model ?? "--"}</div>
      </div>
    </div>
  )
}
