import { useState } from "react"
import { Layout } from "./components/Layout/Layout"
import Home from "./pages/Home"
import Settings from "./pages/Settings"
import Trade from "./pages/Trade"
import Strategy from "./pages/Strategy"
import Backtest from "./pages/Backtest"
import Sentiment from "./pages/Sentiment"
import Risk from "./pages/Risk"

const views = {
  Home,
  Settings,
  Trade,
  Strategy,
  Backtest,
  Sentiment,
  Risk,
}

type ViewKey = keyof typeof views

const NAV_ITEMS: { key: ViewKey; label: string }[] = [
  { key: "Home", label: "Dashboard" },
  { key: "Trade", label: "Trade" },
  { key: "Strategy", label: "Strategy" },
  { key: "Backtest", label: "Backtest" },
  { key: "Risk", label: "Risk" },
  { key: "Sentiment", label: "Sentiment" },
  { key: "Settings", label: "Settings" },
]

function App() {
  const [view, setView] = useState<ViewKey>("Home")
  const ViewComponent = views[view]

  return (
    <Layout navItems={NAV_ITEMS} activeKey={view} onNavigate={(key) => setView(key)}>
      <ViewComponent />
    </Layout>
  )
}

export default App
