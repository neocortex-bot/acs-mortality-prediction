import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "ACS Mortality Risk - Prediksi Mortalitas",
  description: "Prediksi mortalitas pasien ACS menggunakan Random Forest dengan SHAP explanation",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body className="min-h-screen bg-zinc-50 antialiased">{children}</body>
    </html>
  )
}
