import type { ShapFeature } from "@/lib/types"

interface TopContributorsProps {
  features: ShapFeature[]
}

export default function TopContributors({ features }: TopContributorsProps) {
  const maxAbs = Math.max(...features.map((f) => Math.abs(f.shap_contribution)), 0.01)

  return (
    <div className="space-y-3">
      {features.map((f, i) => {
        const isPos = f.direction === "positive"
        const pct = (Math.abs(f.shap_contribution) / maxAbs) * 100
        return (
          <div key={f.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">
                {i + 1}. {f.name}
              </span>
              <span className="text-zinc-500 text-xs">
                = {f.value} ({isPos ? "+" : ""}{f.shap_contribution.toFixed(4)})
              </span>
            </div>
            <div className="w-full bg-zinc-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full ${isPos ? "bg-red-400" : "bg-blue-400"}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
