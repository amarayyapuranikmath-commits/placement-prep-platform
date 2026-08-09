const ResumeSectionScores = ({ sectionScores }) => {
  if (!sectionScores) return null

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <p className="mb-3 text-sm font-medium text-slate-400">Section Scores</p>
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
  )
}

export default ResumeSectionScores
