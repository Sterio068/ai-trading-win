import { useEffect, useState } from "react"
import { fetchRisk, updateRisk, type RiskStatus } from "../../api/risk"

export function RiskPanel() {
  const [risk, setRisk] = useState<RiskStatus | null>(null)
  const [editing, setEditing] = useState<RiskStatus["config"] | null>(null)

  useEffect(() => {
    const load = async () => {
      const status = await fetchRisk()
      setRisk(status)
      setEditing(status.config)
    }
    load()
  }, [])

  const handleChange = (key: keyof RiskStatus["config"], value: string) => {
    setEditing((prev) => ({ ...(prev || risk?.config || {}), [key]: Number(value) }))
  }

  const handleSave = async () => {
    if (!editing) return
    const status = await updateRisk(editing)
    setRisk(status)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Risk Controls</h3>
        <button className="rounded border border-blue-400 px-3 py-1 text-sm" onClick={handleSave}>
          Save
        </button>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {editing &&
          Object.entries(editing).map(([key, value]) => (
            <label key={key} className="text-xs uppercase text-slate-400">
              {key}
              <input
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm"
                value={value}
                onChange={(e) => handleChange(key as keyof RiskStatus["config"], e.target.value)}
                type="number"
              />
            </label>
          ))}
      </div>
      {risk && (
        <div className="mt-6 grid gap-2">
          <div className="text-xs text-muted-foreground">Daily Loss: ${risk.daily_loss.toFixed(2)}</div>
          <div className="text-xs text-muted-foreground">Drawdown: {(risk.drawdown * 100).toFixed(2)}%</div>
          <pre className="max-h-40 overflow-y-auto rounded bg-slate-950/60 p-3 text-xs text-emerald-200">
            {JSON.stringify(risk.exposure, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
