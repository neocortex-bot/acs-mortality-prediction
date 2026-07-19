export interface ShapFeature {
  name: string
  value: number
  shap_contribution: number
  direction: "positive" | "negative"
}

export interface ShapValues {
  base_value: number
  output_space: string
  features: ShapFeature[]
}

export interface TriageInfo {
  label: string
  thresholds: string
  recommendation: string
}

export interface PredictionResult {
  probability: number
  risk_category: "LOW RISK" | "INTERMEDIATE RISK" | "HIGH RISK"
  triage: TriageInfo
  shap_values: ShapValues
  contributors_top3: ShapFeature[]
}

export interface FeatureImportance {
  name: string
  db_column: string
  importance: number
}

export interface FeatureImportanceResponse {
  features: FeatureImportance[]
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
  feature_count: number
}

export interface PatientInput {
  usia: number
  hr: number
  sbp: number
  rr: number
  hb: number
  kalium: number
  ureum: number
  egfr: number
  aptt: number
  lvef: number
  lvot_vti: number
  tapse: number
  killip: 1 | 2 | 3
}
