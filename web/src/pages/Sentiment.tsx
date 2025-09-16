import { useState } from "react"
import { aggregateSentiment } from "../api/sentiment"

export default function Sentiment() {
  const [text, setText] = useState("Bitcoin looks bullish with strong inflows")
  const [result, setResult] = useState<any>(null)

  const handleAnalyze = async () => {
    const data = await aggregateSentiment(text)
    setResult(data)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Sentiment Intelligence</h1>
      <textarea
        className="h-40 w-full rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-sm"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="rounded bg-blue-500 px-3 py-2 text-sm" onClick={handleAnalyze}>
        Analyze
      </button>
      {result && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-sm">
          <div>Label: {result.label}</div>
          <div>Score: {result.score.toFixed(3)}</div>
          <div>Tokens: {result.tokens}</div>
        </div>
      )}
    </div>
  )
}
