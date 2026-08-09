const ResumeKeywords = ({ keywords }) => {
  if (!keywords) return null

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
      <h3 className="text-sm font-semibold text-slate-100">Keyword Analysis</h3>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-400">Strong</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {(keywords.strong || []).map((item, index) => <li key={index}>• {item}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-amber-400">Weak</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {(keywords.weak || []).map((item, index) => <li key={index}>• {item}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-red-400">Missing</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {(keywords.missing || []).map((item, index) => <li key={index}>• {item}</li>)}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ResumeKeywords
