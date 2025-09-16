import { useEffect, useState } from "react";
import { fetchEnv, EnvValues } from "../api/env";
import { fetchBalance } from "../api/broker";
import { executeStrategy } from "../api/strategy";
import { useSettingsStore } from "../store/settings";

const ENV_FIELDS: { key: keyof EnvValues; label: string; type?: string }[] = [
  { key: "MODE", label: "模式" },
  { key: "OPENAI_MODEL_TIER", label: "預設模型" },
  { key: "AI_DAILY_COST_LIMIT_USD", label: "AI 日成本上限", type: "number" },
  { key: "DAILY_INVEST_LIMIT_USDT", label: "每日投資上限", type: "number" },
  { key: "SINGLE_TRADE_LIMIT_USDT", label: "單筆上限", type: "number" },
  { key: "TOTAL_CAPITAL_USDT", label: "總資金", type: "number" },
  { key: "OKX_API_KEY_PAPER", label: "OKX API KEY (PAPER)" },
  { key: "OKX_API_SECRET_PAPER", label: "OKX API SECRET (PAPER)" },
  { key: "OKX_PASSPHRASE_PAPER", label: "OKX PASSPHRASE (PAPER)" },
  { key: "OKX_API_KEY_REAL", label: "OKX API KEY (REAL)" },
  { key: "OKX_API_SECRET_REAL", label: "OKX API SECRET (REAL)" },
  { key: "OKX_PASSPHRASE_REAL", label: "OKX PASSPHRASE (REAL)" },
  { key: "SENTRY_DSN", label: "Sentry DSN" }
];

export default function SettingsPage() {
  const { values, setValue, save, switchMode, loading, error } = useSettingsStore();
  const [aiPing, setAiPing] = useState<any>(null);
  const [balance, setBalance] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchEnv().then((data) => {
      Object.entries(data.values).forEach(([key, value]) => setValue(key, value));
    });
  }, [setValue]);

  const handleSave = async () => {
    setSaving(true);
    await save(values);
    setSaving(false);
  };

  const handleTestBalance = async () => {
    const resp = await fetchBalance();
    setBalance(resp);
  };

  const handleAiPing = async () => {
    const resp = await executeStrategy({ mode: "ping", strategy: "dca", dry_run: true });
    setAiPing(resp);
  };

  return (
    <div className="space-y-6">
      <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
        <div className="text-lg font-semibold text-slate-100">環境設定</div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {ENV_FIELDS.map((field) => (
            <label key={field.key as string} className="flex flex-col text-xs text-slate-400">
              {field.label}
              <input
                type={field.type ?? "text"}
                className="mt-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
                value={values[field.key] ?? ""}
                onChange={(e) => setValue(field.key, e.target.value)}
              />
            </label>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-sky-400 disabled:opacity-50"
          >
            儲存
          </button>
          <button
            onClick={() => switchMode(values.MODE === "paper" ? "real" : "paper")}
            className="rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400"
          >
            切換模式 ({values.MODE})
          </button>
          <button
            onClick={handleTestBalance}
            className="rounded bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400"
          >
            測試連線
          </button>
          <button
            onClick={handleAiPing}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-indigo-400"
          >
            AI Ping
          </button>
        </div>
        {(loading || saving) && <div className="mt-2 text-xs text-slate-500">處理中...</div>}
        {error && <div className="mt-2 text-xs text-rose-400">{error}</div>}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">Balance</div>
          <pre className="mt-2 max-h-52 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {balance ? JSON.stringify(balance, null, 2) : "尚未測試"}
          </pre>
        </div>
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">AI Ping 結果</div>
          <pre className="mt-2 max-h-52 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {aiPing ? JSON.stringify(aiPing, null, 2) : "尚未執行"}
          </pre>
        </div>
      </div>
    </div>
  );
}
