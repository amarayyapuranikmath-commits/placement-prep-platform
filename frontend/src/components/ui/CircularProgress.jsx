// src/components/ui/CircularProgress.jsx
const SIZE_MAP = {
  sm: { box: 56, stroke: 5, font: 'text-xs' },
  md: { box: 88, stroke: 6, font: 'text-lg' },
  lg: { box: 140, stroke: 8, font: 'text-3xl' },
}

const CircularProgress = ({
  value = 0,
  size = 'md',
  label,
  trackColor = '#1e293b',
  progressColor = '#6d5cff',
}) => {
  const { box, stroke, font } = SIZE_MAP[size] || SIZE_MAP.md
  const radius = (box - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const clampedValue = Math.min(Math.max(value, 0), 100)
  const offset = circumference - (clampedValue / 100) * circumference

  return (
    <div className="relative inline-flex flex-col items-center justify-center">
      <svg width={box} height={box} viewBox={`0 0 ${box} ${box}`} className="-rotate-90">
        <circle
          cx={box / 2}
          cy={box / 2}
          r={radius}
          fill="none"
          stroke={trackColor}
          strokeWidth={stroke}
        />
        <circle
          cx={box / 2}
          cy={box / 2}
          r={radius}
          fill="none"
          stroke={progressColor}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-semibold text-slate-100 ${font}`}>{clampedValue}%</span>
        {label && <span className="mt-0.5 text-[10px] text-slate-500">{label}</span>}
      </div>
    </div>
  )
}

export default CircularProgress