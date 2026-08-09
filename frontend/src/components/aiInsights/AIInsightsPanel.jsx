import { motion } from 'framer-motion'
import { ArrowRight, RefreshCw, Sparkles } from 'lucide-react'

const Pill = ({ text }) => (
  <span className="rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs text-slate-300">{text}</span>
)

const AIInsightsPanel = ({ title, description, actionText, actionHref, children, withBorder }) => {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`rounded-[28px] ${withBorder ? 'border border-slate-800 bg-slate-950/80' : 'bg-slate-900/85'} p-6 shadow-glass`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-slate-400">
            <Sparkles size={16} />
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">{title}</p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-slate-100">{description}</h2>
          </div>
        </div>
        {actionText && actionHref && (
          <a
            href={actionHref}
            className="inline-flex items-center rounded-2xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-violet-500/40 hover:text-violet-300"
          >
            {actionText}
            <ArrowRight size={16} className="ml-2" />
          </a>
        )}
      </div>
      {children}
    </motion.section>
  )
}

export default AIInsightsPanel
