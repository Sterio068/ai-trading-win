import { useState } from "react";
import { aggregateSentiment } from "../api/sentiment";

export default function SentimentPage() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    const texts = input.split("\n").filter(Boolean);
    const resp = await aggregateSentiment(texts);
    setResult(resp);
  };

  return (
    <div className="space-y-6">
      <div className="rounded border border-slate-800 bg-slate-900/60 p-6">
        <div className="text-sm font-semibold text-slate-200">輸入文本</div>
        <textarea
          rows={8}
          className="mt-3 w-full rounded bg-slate-900 px-3 py-2 text-sm text-slate-100"
          placeholder="輸入多段文本，每行一段"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          onClick={handleAnalyze}
          className="mt-4 rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-indigo-400"
        >
          分析情緒
        </button>
      </div>
      {result && (
        <div className="rounded border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
          <div className="text-slate-200">結果</div>
          <div className="mt-2 grid gap-2 md:grid-cols-3">
            <div className="rounded bg-slate-900/80 p-3">
              <div className="text-xs text-slate-400">Score</div>
              <div className="text-lg text-sky-400">{result.score}</div>
            </div>
            <div className="rounded bg-slate-900/80 p-3">
              <div className="text-xs text-slate-400">Positive</div>
              <div className="text-lg text-emerald-400">{result.positive}</div>
            </div>
            <div className="rounded bg-slate-900/80 p-3">
              <div className="text-xs text-slate-400">Negative</div>
              <div className="text-lg text-rose-400">{result.negative}</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-slate-400">摘要：{result.summary}</div>
        </div>
      )}
    </div>
  );
}
