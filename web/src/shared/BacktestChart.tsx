import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface BacktestChartProps {
  data: number[];
}

export function BacktestChart({ data }: BacktestChartProps) {
  const formatted = data.map((value, index) => ({ index, value }));
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={formatted}>
          <XAxis dataKey="index" stroke="#94a3b8" hide />
          <YAxis stroke="#94a3b8" domain={["auto", "auto"]} width={50} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} />
          <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
