import { FiCheckCircle, FiAlertCircle, FiTarget, FiZap } from 'react-icons/fi'

const Section = ({ icon: Icon, iconClass, title, items, emptyText }) => (
  <div className="h-full rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
    <div className="mb-3 flex items-center gap-2">
      <Icon size={16} className={iconClass} />
      <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
    </div>
    {items && items.length > 0 ? (
      <ul className="space-y-1">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
            <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-slate-600" />
            {item}
          </li>
        ))}
      </ul>
    ) : (
      <p className="text-sm text-slate-600">{emptyText}</p>
    )}
  </div>
)

const AIAnalysisCards = ({ strengths, weaknesses, missingSkills, suggestions, keywords }) => {
  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 items-stretch">
        <Section
          icon={FiCheckCircle}
          iconClass="text-emerald-400"
          title="Strengths"
          items={strengths}
          emptyText="No strengths identified yet."
        />
        <Section
          icon={FiAlertCircle}
          iconClass="text-amber-400"
          title="Weaknesses"
          items={weaknesses}
          emptyText="No weaknesses identified yet."
        />
        <Section
          icon={FiTarget}
          iconClass="text-red-400"
          title="Missing Skills"
          items={missingSkills}
          emptyText="No missing skills identified."
        />
        <Section
          icon={FiZap}
          iconClass="text-accent"
          title="Improvement Suggestions"
          items={suggestions}
          emptyText="No suggestions available."
        />
      </div>

      {keywords && (
        <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
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
      )}
    </div>
  )
}

export default AIAnalysisCards