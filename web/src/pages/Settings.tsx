import { useEffect, useMemo, useState } from "react"
import { useSettingsStore } from "../store/settings"

const SECRET_KEYS = ["OKX_API_KEY_PAPER", "OKX_API_SECRET_PAPER", "OKX_API_PASSPHRASE_PAPER", "OKX_API_KEY_REAL", "OKX_API_SECRET_REAL", "OKX_API_PASSPHRASE_REAL", "OPENAI_API_KEY"]

export default function Settings() {
  const { env, load, save, toggleMode, mode, loading } = useSettingsStore()
  const [draft, setDraft] = useState(env)

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    setDraft(env)
  }, [env])

  const grouped = useMemo(() => {
    return Object.entries(draft).reduce<Record<string, [string, string][]>>((acc, [key, value]) => {
      const group = key.startsWith("OKX") ? "OKX" : key.startsWith("AI") || key.startsWith("OPENAI") ? "AI" : "Core"
      acc[group] = acc[group] || []
      acc[group].push([key, value])
      return acc
    }, {})
  }, [draft])

  const handleChange = (key: string, value: string) => {
    setDraft((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    const changes = Object.fromEntries(
      Object.entries(draft).filter(([key, value]) => value !== env[key])
    )
    if (Object.keys(changes).length === 0) return
    await save(changes)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground">Manage environment variables and connectivity.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Mode:</span>
          <button
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-sm hover:bg-slate-800"
            onClick={() => toggleMode(mode === "PAPER" ? "REAL" : "PAPER")}
          >
            {mode}
          </button>
          <button
            className="rounded-lg border border-blue-500 bg-blue-500 px-3 py-1 text-sm font-semibold text-white shadow"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(grouped).map(([group, items]) => (
          <div key={group} className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <h2 className="mb-4 text-lg font-semibold">{group}</h2>
            <div className="space-y-3">
              {items.map(([key, value]) => (
                <label key={key} className="block text-xs uppercase tracking-wide text-slate-400">
                  {key}
                  <input
                    className="mt-1 w-full rounded border border-slate-700 bg-slate-950/70 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
                    type={SECRET_KEYS.includes(key) ? "password" : "text"}
                    value={value ?? ""}
                    onChange={(e) => handleChange(key, e.target.value)}
                  />
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
