"use client"

import { useState } from "react"
import Header from "@/components/header"
import PatientForm from "@/components/patient-form"
import ResultsPanel from "@/components/results-panel"
import type { PatientInput, PredictionResult } from "@/lib/types"
import { predict } from "@/lib/api"

export default function Home() {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async (data: PatientInput) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predict(data)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menghubungi server")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <PatientForm onPredict={handlePredict} loading={loading} />
          </div>
          <div>
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 mb-6">
                {error}
              </div>
            )}
            {loading && (
              <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-900" />
              </div>
            )}
            {result && !loading && <ResultsPanel result={result} />}
            {!result && !loading && !error && (
              <div className="flex items-center justify-center h-full py-20">
                <p className="text-zinc-400 text-center">
                  Masukkan data pasien dan tekan <br />
                  <strong>"Prediksi Risiko"</strong> untuk melihat hasil
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
