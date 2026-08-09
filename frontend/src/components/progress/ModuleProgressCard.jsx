import { motion } from 'framer-motion'

const getStatusTone = (status) => {
  const normalized = String(status || '').toLowerCase()
  if (normalized.includes('complete') || normalized.includes('done')) return 'bg-emerald-400'
  if (normalized.includes('progress') || normalized.includes('in')) return 'bg-amber-400'
  return 'bg-slate-500'
}

const ModuleProgressCard = ({ module, progress, status, detail, icon: Icon }) => {
  const safeProgress = Math.min(100, Math.max(0, Number(progress) || 0))
  const statusTone = getStatusTone(status)

  return (
    <motion.article
      whileHover={{ y: -1, scale: 1.005 }}
      transition={{ duration: 0.2 }}
      className="rounded-2xl border border-slate-800 bg-slate-950/80 p-3"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-start gap-2">
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-slate-300">
            <Icon size={14} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-white">{module}</p>
            <div className="mt-1 flex items-center gap-1.5 text-[11px] text-slate-500">
              <span className={`h-1.5 w-1.5 rounded-full ${statusTone}`} />
              <span>{status || 'Pending'}</span>
            </div>
          </div>
        </div>
        <span className="text-sm font-semibold text-slate-100">{safeProgress}%</span>
      </div>

      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-gradient-to-r from-accent to-cyan-400 transition-all duration-500" style={{ width: `${safeProgress}%` }} />
      </div>

      <p className="mt-2 text-xs text-slate-500">{detail || 'No additional data yet'}</p>
    </motion.article>
  )
}

export default ModuleProgressCard
