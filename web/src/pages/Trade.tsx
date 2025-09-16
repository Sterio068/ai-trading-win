import { useEffect, useState } from "react"
import { fetchBalance } from "../api/broker"
import { OrderForm } from "../components/OrderForm"
import { OcoForm } from "../components/OcoForm"

export default function Trade() {
  const [balance, setBalance] = useState<any>(null)

  useEffect(() => {
    const load = async () => {
      const data = await fetchBalance()
      setBalance(data)
    }
    load()
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Trade Console</h1>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <OrderForm />
          <OcoForm />
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h3 className="text-lg font-semibold">Balance</h3>
          <pre className="mt-3 max-h-80 overflow-y-auto rounded bg-slate-950/60 p-3 text-xs text-emerald-200">
            {JSON.stringify(balance, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}
