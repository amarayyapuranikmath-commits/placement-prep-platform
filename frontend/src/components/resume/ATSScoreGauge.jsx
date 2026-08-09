const clamp = (v, a = 0, b = 100) => Math.max(a, Math.min(b, v))

const Circular = ({ value = 0, size = 96, stroke = 8 }) => {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const v = clamp(value, 0, 100)
  const dash = `${(v / 100) * c} ${c}`
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <g transform={`translate(${size / 2}, ${size / 2})`}>
        <circle r={r} cx="0" cy="0" fill="none" stroke="#0f172a" strokeWidth={stroke} />
        <circle r={r} cx="0" cy="0" fill="none" stroke="#60a5fa" strokeWidth={stroke} strokeLinecap="round" strokeDasharray={dash} transform="rotate(-90)" />
      </g>
    </svg>
  )
}

const ATSScoreGauge = ({ score = null, qualityLabel = 'N/A' }) => {
  const hasScore = score !== null && score !== undefined
  const displayScore = hasScore ? Math.round(score) : null
  return (
    <div className="w-[300px] h-full rounded-2xl border border-slate-700 bg-slate-900/80 p-4 flex flex-col justify-center">
      <h2 className="text-sm font-semibold mb-3 text-slate-100">ATS Score</h2>

      <div className="flex items-center gap-4">
        <div className="flex-shrink-0">
          <Circular value={displayScore} size={88} stroke={8} />
        </div>
        <div>
          <div className="text-3xl font-bold text-blue-400">{hasScore ? displayScore : '--'}</div>
          <div className="mt-1 text-xs text-slate-400">{hasScore ? qualityLabel : 'Not analyzed yet'}</div>
        </div>
      </div>
    </div>
  )
}

export default ATSScoreGauge