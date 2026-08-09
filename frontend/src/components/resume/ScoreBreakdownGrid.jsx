const CATEGORIES = [
  { key: 'keywords', label: 'Keywords' },
  { key: 'formatting', label: 'Formatting' },
  { key: 'skills', label: 'Skills' },
  { key: 'projects', label: 'Projects' },
  { key: 'experience', label: 'Experience' },
  { key: 'education', label: 'Education' },
]

const getBarColor = (value) => {
  if (value >= 80) return 'bg-emerald-500'
  if (value >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

const ScoreBreakdownGrid = ({ breakdown, roleMatch, keywordMatch, sectionScores, hideSectionScores = false }) => {
  if (!breakdown) return null
  return (
      <div className="h-full rounded-2xl border border-slate-800 bg-slate-900/70 p-4 flex flex-col">
      <p className="mb-5 text-sm font-medium text-slate-400">Resume Insights</p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CATEGORIES.map(({ key, label }) => {
          const value = breakdown[key] ?? 0
          return (
              <div key={key} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{label}</span>
                <span className="text-xs font-semibold text-slate-200">{value}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${getBarColor(value)}`}
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Role Match</p>
            <p className="mt-1 text-xl font-semibold text-slate-100">{roleMatch ?? 0}%</p>
        </div>
          <div className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Keyword Match</p>
            <p className="mt-1 text-xl font-semibold text-slate-100">{keywordMatch ?? 0}%</p>
        </div>
      </div>

      {!hideSectionScores && sectionScores && (
        <div className="mt-5">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Section Scores</p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {Object.entries(sectionScores).map(([key, value]) => (
                <div key={key} className="rounded-md border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="font-medium text-slate-100">{value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ScoreBreakdownGrid