"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from "recharts"
import type { ShapFeature } from "@/lib/types"

interface ShapWaterfallProps {
  baseValue: number
  features: ShapFeature[]
}

export default function ShapWaterfall({ baseValue, features }: ShapWaterfallProps) {
  const data = features.map((f) => ({
    name: f.name,
    value: f.shap_contribution,
    absValue: Math.abs(f.shap_contribution),
    fill: f.direction === "positive" ? "#ef4444" : "#3b82f6",
  }))

  return (
    <div className="pt-2">
      <p className="text-xs text-zinc-400 mb-2">
        Base value: <strong>{baseValue.toFixed(4)}</strong> (expected probability)
      </p>
      <ResponsiveContainer width="100%" height={360}>
        <BarChart data={data} layout="vertical" margin={{ left: 60, right: 40, top: 5, bottom: 5 }}>
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={70} />
          <Tooltip
            formatter={(value: number) => [`${value >= 0 ? "+" : ""}${value.toFixed(4)}`, "SHAP"]}
          />
          <Bar dataKey="value" barSize={16}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
