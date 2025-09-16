import { useEffect, useState } from "react";
import { fetchRiskConfig, fetchRiskState, fetchRiskVersion, updateRiskConfig } from "../api/risk";
import { RiskPanel } from "../components/RiskPanel";

export default function RiskPage() {
  const [config, setConfig] = useState<string>("{}");
  const [state, setState] = useState<Record<string, any> | null>(null);
  const [version, setVersion] = useState<Record<string, any> | null>(null);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    fetchRiskConfig().then((data) => setConfig(JSON.stringify(data, null, 2)));
    fetchRiskState().then(setState);
    fetchRiskVersion().then(setVersion);
  }, []);

  const handleSave = async () => {
    try {
      const parsed = JSON.parse(config);
      const resp = await updateRiskConfig(parsed);
      setMessage(`更新成功 version=${resp.version}`);
      fetchRiskState().then(setState);
      fetchRiskVersion().then(setVersion);
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[1fr,1fr]">
      <div className="space-y-4">
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-sm font-semibold text-slate-200">風控設定</div>
          <textarea
            rows={16}
            className="mt-3 w-full rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
            value={config}
            onChange={(e) => setConfig(e.target.value)}
          />
          <button
            onClick={handleSave}
            className="mt-4 rounded bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-sky-400"
          >
            儲存設定
          </button>
          {message && <div className="mt-2 text-xs text-slate-400">{message}</div>}
        </div>
        <div className="rounded border border-slate-800 bg-slate-900/60 p-4 text-xs text-slate-400">
          <div className="text-sm font-semibold text-slate-200">版本資訊</div>
          <pre className="mt-2 max-h-64 overflow-auto rounded bg-slate-900/80 p-3 text-xs text-slate-300">
            {version ? JSON.stringify(version, null, 2) : "載入中"}
          </pre>
        </div>
      </div>
      <RiskPanel state={state} />
    </div>
  );
}
