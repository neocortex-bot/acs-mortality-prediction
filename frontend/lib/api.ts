import type { PredictionResult, FeatureImportanceResponse, HealthResponse, PatientInput } from "./types"

function getApiBase(): string {
  if (typeof window !== "undefined") {
    // In production, check if we're on the public domain
    if (window.location.hostname === "igdacs.studipustaka.org") {
      return "https://api-igdacs.studipustaka.org"
    }
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${getApiBase()}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API error ${res.status}: ${body}`)
  }
  return res.json()
}

export async function predict(data: PatientInput): Promise<PredictionResult> {
  return fetchApi<PredictionResult>("/predict", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>("/health")
}

export async function getFeatureImportance(): Promise<FeatureImportanceResponse> {
  return fetchApi<FeatureImportanceResponse>("/feature_importance")
}

export async function getThresholds(): Promise<Record<string, unknown>> {
  return fetchApi("/thresholds")
}
