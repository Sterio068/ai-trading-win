import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import type { BacktestResult } from "../api/backtest"

interface Props {
  data: BacktestResult | null
}

export function BacktestChart({ data }: Props) {
  if (!data) {
    return <div className="h-64 flex items-center justify-center text-muted-foreground">No data</div>
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.equity}>
          <XAxis dataKey="ts" hide />
          <YAxis domain={["auto", "auto"]} tickFormatter={(value) => `$${value.toFixed(0)}`} />
          <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
          <Line type="monotone" dataKey="value" stroke="#60a5fa" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
