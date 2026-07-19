"use client"

import type { PredictionResult } from "@/lib/types"
import RiskBadge from "./risk-badge"
import ProbabilityGauge from "./probability-gauge"
import TopContributors from "./top-contributors"
import ShapWaterfall from "./shap-waterfall"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

interface ResultsPanelProps {
  result: PredictionResult
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  return (
    <div className="space-y-6">
      <RiskBadge category={result.risk_category} label={result.triage.label} />

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Risk Probability</CardTitle>
        </CardHeader>
        <CardContent>
          <ProbabilityGauge probability={result.probability} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Top 3 Contributors</CardTitle>
        </CardHeader>
        <CardContent>
          <TopContributors features={result.contributors_top3} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">SHAP Waterfall</CardTitle>
        </CardHeader>
        <CardContent>
          <ShapWaterfall
            baseValue={result.shap_values.base_value}
            features={result.shap_values.features}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Triage Recommendation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-zinc-600">{result.triage.recommendation}</p>
          <p className="text-xs text-zinc-400 mt-1">Thresholds: {result.triage.thresholds}</p>
        </CardContent>
      </Card>
    </div>
  )
}
