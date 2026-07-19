interface ProbabilityGaugeProps {
  probability: number
}

export default function ProbabilityGauge({ probability }: ProbabilityGaugeProps) {
  const pct = (probability * 100).toFixed(1)
  const color =
    probability < 0.069 ? "bg-emerald-500" :
    probability < 0.279 ? "bg-amber-500" : "bg-red-500"

  return (
    <div className="text-center py-4">
      <div className="text-4xl font-bold tracking-tight">{pct}%</div>
      <div className="text-sm text-zinc-500 mt-1">Predicted Mortality Risk</div>
      <div className="w-full bg-zinc-100 rounded-full h-3 mt-3 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${Math.min(probability * 100, 100)}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-zinc-400 mt-1">
        <span>0%</span>
        <span>6.9%</span>
        <span>27.9%</span>
        <span>100%</span>
      </div>
    </div>
  )
}
