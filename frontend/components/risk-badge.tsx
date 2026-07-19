import { Badge } from "@/components/ui/badge"

interface RiskBadgeProps {
  category: string
  label: string
}

export default function RiskBadge({ category, label }: RiskBadgeProps) {
  const variant =
    category === "LOW RISK" ? "success" :
    category === "INTERMEDIATE RISK" ? "warning" : "danger"

  const colorClass =
    category === "LOW RISK" ? "text-emerald-700 bg-emerald-50 border-emerald-200" :
    category === "INTERMEDIATE RISK" ? "text-amber-700 bg-amber-50 border-amber-200" :
    "text-red-700 bg-red-50 border-red-200"

  return (
    <div className={`rounded-lg border-2 p-4 text-center ${colorClass}`}>
      <div className="text-xs font-medium uppercase tracking-wide mb-1">{category}</div>
      <div className="text-lg font-bold">{label}</div>
    </div>
  )
}
