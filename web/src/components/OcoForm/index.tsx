import { useState } from "react";

export interface OcoParams {
  sl_pct: number;
  tp_pct: number;
}

interface OcoFormProps {
  onSubmit: (params: OcoParams) => void;
}

export function OcoForm({ onSubmit }: OcoFormProps) {
  const [form, setForm] = useState<OcoParams>({ sl_pct: 0.01, tp_pct: 0.02 });
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <div className="text-sm font-semibold text-slate-200">OCO 設定</div>
      <div className="mt-3 grid gap-2 md:grid-cols-2">
        <label className="flex flex-col text-xs text-slate-400">
          止損 (%)
          <input
            type="number"
            step="0.001"
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.sl_pct}
            onChange={(e) => setForm((prev) => ({ ...prev, sl_pct: Number(e.target.value) }))}
          />
        </label>
        <label className="flex flex-col text-xs text-slate-400">
          止盈 (%)
          <input
            type="number"
            step="0.001"
            className="mt-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-100"
            value={form.tp_pct}
            onChange={(e) => setForm((prev) => ({ ...prev, tp_pct: Number(e.target.value) }))}
          />
        </label>
      </div>
      <button
        onClick={() => onSubmit(form)}
        className="mt-4 w-full rounded bg-emerald-500 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400"
      >
        套用 OCO
      </button>
    </div>
  );
}
