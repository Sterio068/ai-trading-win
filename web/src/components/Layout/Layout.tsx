import type { ReactNode } from "react"
import { useAutopilotStore } from "../../store/autopilot"

interface NavItem {
  key: string
  label: string
}

interface LayoutProps {
  navItems: NavItem[]
  activeKey: string
  onNavigate: (key: NavItem["key"]) => void
  children: ReactNode
}

export function Layout({ navItems, activeKey, onNavigate, children }: LayoutProps) {
  const { status } = useAutopilotStore()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="container mx-auto flex items-center justify-between py-4">
          <div>
            <h1 className="text-xl font-semibold text-white">AI Quant Trading</h1>
            <p className="text-xs text-muted-foreground">Autopilot {status?.active ? "ON" : "OFF"}</p>
          </div>
          <nav className="flex gap-2">
            {navItems.map((item) => (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className={`rounded-lg px-3 py-1 text-sm ${
                  activeKey === item.key
                    ? "bg-blue-500 text-white shadow"
                    : "bg-slate-800 text-slate-200 hover:bg-slate-700"
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="container mx-auto py-6">{children}</main>
    </div>
  )
}
