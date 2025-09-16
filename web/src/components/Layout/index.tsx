import type { ReactNode } from "react";
import { Menu, Settings, LineChart, Activity, Bot, Shield, SlidersHorizontal } from "lucide-react";

interface NavItem {
  id: string;
  label: string;
  icon?: ReactNode;
}

interface LayoutProps {
  navItems: NavItem[];
  active: string;
  onNavigate: (id: string) => void;
  children: ReactNode;
}

const iconMap: Record<string, ReactNode> = {
  home: <Bot className="h-4 w-4" />,
  settings: <Settings className="h-4 w-4" />,
  trade: <SlidersHorizontal className="h-4 w-4" />,
  strategy: <LineChart className="h-4 w-4" />,
  backtest: <Activity className="h-4 w-4" />,
  sentiment: <Menu className="h-4 w-4" />,
  risk: <Shield className="h-4 w-4" />
};

export function Layout({ navItems, active, onNavigate, children }: LayoutProps) {
  const appVersion =
    typeof window !== "undefined"
      ? String((window as any).__APP_VERSION__ ?? "dev")
      : "dev";
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <aside className="hidden w-60 flex-col border-r border-slate-800 bg-slate-900/40 p-4 md:flex">
        <div className="mb-6 text-lg font-semibold tracking-wide text-slate-200">AI Trading</div>
        <nav className="flex flex-1 flex-col gap-2">
          {navItems.map((item) => {
            const icon = item.icon ?? iconMap[item.id] ?? <Menu className="h-4 w-4" />;
            const isActive = item.id === active;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition hover:bg-slate-800/80 ${
                  isActive ? "bg-slate-800 text-sky-300" : "text-slate-300"
                }`}
              >
                {icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <footer className="mt-6 text-xs text-slate-500">版本 {appVersion}</footer>
      </aside>
      <main className="flex-1">
        <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-900/70 backdrop-blur">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="font-semibold capitalize text-slate-200">{active}</div>
            <div className="text-xs text-slate-400">API: {import.meta.env.VITE_API ?? "http://127.0.0.1:8000"}</div>
          </div>
        </header>
        <div className="p-4 md:p-6">{children}</div>
      </main>
    </div>
  );
}
