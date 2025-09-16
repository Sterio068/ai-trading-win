import { useEffect, useMemo, useState } from "react";
import { Layout } from "./components/Layout";
import HomePage from "./pages/Home";
import SettingsPage from "./pages/Settings";
import TradePage from "./pages/Trade";
import StrategyPage from "./pages/Strategy";
import BacktestPage from "./pages/Backtest";
import SentimentPage from "./pages/Sentiment";
import RiskPage from "./pages/Risk";
import { useSettingsStore } from "./store/settings";
import { useWsStore } from "./store/ws";
import { useAutopilotStore } from "./store/autopilot";

const NAV_ITEMS = [
  { id: "home", label: "Autopilot" },
  { id: "settings", label: "Settings" },
  { id: "trade", label: "Trade" },
  { id: "strategy", label: "Strategy" },
  { id: "backtest", label: "Backtest" },
  { id: "sentiment", label: "Sentiment" },
  { id: "risk", label: "Risk" }
];

const PAGE_COMPONENTS: Record<string, JSX.Element> = {
  home: <HomePage />,
  settings: <SettingsPage />,
  trade: <TradePage />,
  strategy: <StrategyPage />,
  backtest: <BacktestPage />,
  sentiment: <SentimentPage />,
  risk: <RiskPage />
};

function App() {
  const [active, setActive] = useState("home");
  const fetchEnv = useSettingsStore((state) => state.fetch);
  const connectWs = useWsStore((state) => state.connect);
  const messages = useWsStore((state) => state.messages);
  const updateAutopilot = useAutopilotStore((state) => state.updateFromWs);

  useEffect(() => {
    fetchEnv();
    connectWs();
  }, [fetchEnv, connectWs]);

  useEffect(() => {
    const latest = messages[messages.length - 1];
    if (!latest) return;
    if (latest.topic === "autopilot") {
      updateAutopilot(latest.payload as Record<string, unknown>);
    }
  }, [messages, updateAutopilot]);

  const page = useMemo(() => PAGE_COMPONENTS[active] ?? <HomePage />, [active]);

  return (
    <Layout navItems={NAV_ITEMS} active={active} onNavigate={setActive}>
      {page}
    </Layout>
  );
}

export default App;
