const DIFFICULTY_STYLES = {
  easy: 'bg-emerald-500/10 text-emerald-400',
  medium: 'bg-amber-500/10 text-amber-400',
  hard: 'bg-red-500/10 text-red-400',
}

const DifficultyBadge = ({ difficulty }) => {
  const styles = DIFFICULTY_STYLES[difficulty] || 'bg-slate-800 text-slate-400'

  return (
    <span
      className={`inline-block rounded-full px-2.5 py-1 text-xs font-medium capitalize ${styles}`}
    >
      {difficulty}
    </span>
  )
}

export default DifficultyBadge