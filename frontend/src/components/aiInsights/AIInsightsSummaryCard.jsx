import { CheckCircle2, AlertTriangle, Sparkles, CircleDot, ShieldCheck } from 'lucide-react'

const ICONS = {
  overview: Sparkles,
  progress: CircleDot,
  strengths: ShieldCheck,
  weaknesses: AlertTriangle,
  observation: CheckCircle2,
}

const sectionOrder = ['overview', 'progress', 'strengths', 'weaknesses', 'observation']

const AIInsightsSummaryCard = ({ summary }) => {
  return (
    <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="space-y-4">
        {sectionOrder.map((sectionKey) => {
          const section = summary?.[sectionKey]
          if (!section) return null
          const Icon = ICONS[sectionKey]

          return (
            <div key={sectionKey} className="flex gap-4 pt-2">
              <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
                <Icon size={18} />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-100 uppercase tracking-[0.2em] text-slate-400">
                  {section.title}
                </p>
                <p className="text-sm leading-7 text-slate-300">{section.content}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AIInsightsSummaryCard
