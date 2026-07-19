export default function Header() {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-zinc-900">ACS Mortality Risk</h1>
          <p className="text-sm text-zinc-500">Prediksi Mortalitas Pasien ACS — Makassar ACS Registry</p>
        </div>
        <a
          href="https://github.com/neocortex-bot/acs-mortality-prediction"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-zinc-400 hover:text-zinc-600 transition-colors underline underline-offset-2"
        >
          GitHub
        </a>
      </div>
    </header>
  )
}
