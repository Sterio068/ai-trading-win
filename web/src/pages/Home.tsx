import { useEffect } from "react"
import { useAutopilotStore } from "../store/autopilot"
import { useSettingsStore } from "../store/settings"

function StatCard({ title, value, description }: { title: string; value: string; description: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="text-2xl font-semibold text-white">{value}</div>
      <div className="text-xs text-muted-foreground mt-2">{description}</div>
    </div>
  )
}

export default function Home() {
  const { status, load } = useAutopilotStore()
  const { env, load: loadEnv } = useSettingsStore()

  useEffect(() => {
    load()
    loadEnv()
  }, [load, loadEnv])

  const remainingCost =
    typeof status?.daily_cost?.remaining === "number" ? `$${status.daily_cost.remaining.toFixed(2)}` : "--"

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">AI Autopilot Overview</h1>
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Active Mode"
          value={status?.active ? "Autopilot" : "Manual"}
          description={`Next run: ${status?.next_run ?? "--"}`}
        />
        <StatCard
          title="Model Tier"
          value={status?.last_model ?? env.OPENAI_MODEL_TIER ?? "gpt-5-nano"}
          description={`Last run: ${status?.last_run ?? "--"}`}
        />
        <StatCard
          title="AI Cost Remaining"
          value={remainingCost}
          description={`Daily limit: $${env.AI_DAILY_COST_LIMIT_USD ?? "--"}`}
        />
      </div>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-xl font-semibold mb-4">Latest Orders</h2>
        <p className="text-sm text-muted-foreground">
          Review AI generated orders and ensure capital allocation aligns with your risk appetite.
        </p>
        <pre className="mt-4 max-h-64 overflow-y-auto rounded bg-slate-950/60 p-4 text-xs text-emerald-200">
          {JSON.stringify(status?.last_orders ?? [], null, 2)}
        </pre>
      </div>
    </div>
  )
}
