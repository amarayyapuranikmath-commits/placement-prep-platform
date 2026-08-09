import { FiFileText, FiChevronRight } from 'react-icons/fi'

const formatDate = (isoString) => {
  if (!isoString) return '—'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(isoString))
}

const ResumeHistoryList = ({ history, activeResumeId, onView }) => {
  if (!history || history.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 text-center">
        <p className="text-sm text-slate-500">No previous resume versions yet.</p>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
      <p className="mb-3 text-sm font-medium text-slate-400">Resume History</p>
      <ul className="divide-y divide-slate-800">
        {history.map((item) => (
          <li key={item.id} className="flex items-center justify-between py-2 first:pt-0 last:pb-0">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-950/60 text-slate-500">
                <FiFileText size={15} />
              </span>
              <div>
                <p className="text-sm text-slate-200">
                  Version {item.version}
                  {item.id === activeResumeId && (
                    <span className="ml-2 rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                      Current
                    </span>
                  )}
                </p>
                <p className="text-xs text-slate-500">{formatDate(item.uploaded_at)}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {item.ats_score !== null && item.ats_score !== undefined && (
                <span className="text-sm font-semibold text-slate-200">{item.ats_score}%</span>
              )}
              <button
                type="button"
                onClick={() => onView(item.id)}
                className="flex items-center gap-1 text-xs font-medium text-accent transition-opacity hover:opacity-80"
              >
                View <FiChevronRight size={13} />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default ResumeHistoryList