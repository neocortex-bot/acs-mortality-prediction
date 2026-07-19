"use client"

import { useState } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import type { PatientInput } from "@/lib/types"

interface FormSection {
  title: string
  fields: {
    key: keyof PatientInput
    label: string
    unit: string
    min: number
    max: number
    step?: string
    type?: "number" | "select"
    options?: { value: number; label: string }[]
  }[]
}

const sections: FormSection[] = [
  {
    title: "Data Klinis",
    fields: [
      { key: "usia", label: "Usia", unit: "tahun", min: 18, max: 95 },
      { key: "killip", label: "Killip Class", unit: "", min: 1, max: 3, type: "select", options: [{ value: 1, label: "Killip I" }, { value: 2, label: "Killip II" }, { value: 3, label: "Killip III" }] },
    ],
  },
  {
    title: "Tanda Vital",
    fields: [
      { key: "hr", label: "Heart Rate", unit: "bpm", min: 40, max: 200 },
      { key: "sbp", label: "SBP", unit: "mmHg", min: 60, max: 220 },
      { key: "rr", label: "Respiratory Rate", unit: "/min", min: 8, max: 50 },
    ],
  },
  {
    title: "Laboratorium",
    fields: [
      { key: "hb", label: "Hemoglobin", unit: "g/dL", min: 5, max: 18, step: "0.1" },
      { key: "kalium", label: "Kalium (K+)", unit: "mEq/L", min: 2, max: 7, step: "0.1" },
      { key: "ureum", label: "Ureum", unit: "mg/dL", min: 5, max: 250 },
      { key: "egfr", label: "eGFR", unit: "mL/min/1.73m²", min: 5, max: 150 },
      { key: "aptt", label: "APTT", unit: "detik", min: 15, max: 120 },
    ],
  },
  {
    title: "Ekokardiografi",
    fields: [
      { key: "lvef", label: "LVEF", unit: "%", min: 15, max: 75 },
      { key: "lvot_vti", label: "LVOT VTI", unit: "cm", min: 5, max: 35, step: "0.1" },
      { key: "tapse", label: "TAPSE", unit: "mm", min: 0.8, max: 3.5, step: "0.1" },
    ],
  },
]

interface PatientFormProps {
  onPredict: (data: PatientInput) => void
  loading: boolean
}

export default function PatientForm({ onPredict, loading }: PatientFormProps) {
  const [form, setForm] = useState<PatientInput>({
    usia: 60,
    hr: 80,
    sbp: 130,
    rr: 20,
    hb: 13,
    kalium: 4,
    ureum: 40,
    egfr: 70,
    aptt: 35,
    lvef: 45,
    lvot_vti: 18,
    tapse: 2.0,
    killip: 1,
  })

  const update = (key: keyof PatientInput, value: string) => {
    const num = key === "killip" ? parseInt(value) : parseFloat(value)
    if (!isNaN(num)) setForm((prev) => ({ ...prev, [key]: num }))
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onPredict(form)
      }}
      className="space-y-6"
    >
      {sections.map((section) => (
        <Card key={section.title}>
          <div className="px-6 pt-4 pb-2 border-b border-zinc-100">
            <h3 className="font-semibold text-sm text-zinc-700">{section.title}</h3>
          </div>
          <CardContent className="pt-4 space-y-4">
            {section.fields.map((field) => (
              <div key={field.key} className="space-y-1.5">
                <Label htmlFor={field.key}>
                  {field.label} {field.unit && <span className="text-zinc-400 font-normal">({field.unit})</span>}
                </Label>
                {field.type === "select" ? (
                  <Select
                    id={field.key}
                    value={String(form[field.key])}
                    onChange={(e) => update(field.key, e.target.value)}
                  >
                    {field.options?.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>
                ) : (
                  <Input
                    id={field.key}
                    type="number"
                    step={field.step || "1"}
                    min={field.min}
                    max={field.max}
                    value={form[field.key]}
                    onChange={(e) => update(field.key, e.target.value)}
                  />
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      ))}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "Memproses..." : "Prediksi Risiko"}
      </Button>
    </form>
  )
}
