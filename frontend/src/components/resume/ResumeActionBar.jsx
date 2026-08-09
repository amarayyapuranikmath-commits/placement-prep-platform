import { FiRefreshCw, FiUploadCloud, FiTrash2 } from 'react-icons/fi'

const ResumeActionBar = ({ onReanalyze, onReplace, onDelete, isBusy }) => {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        onClick={onReanalyze}
        disabled={isBusy}
        className="flex items-center gap-2 rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <FiRefreshCw size={14} /> Analyze Again
      </button>
      <button
        type="button"
        onClick={onReplace}
        disabled={isBusy}
        className="flex items-center gap-2 rounded-md border border-slate-700 px-3 py-1.5 text-sm font-medium text-slate-200 transition-colors hover:border-accent/50 hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
      >
        <FiUploadCloud size={14} /> Replace Resume
      </button>
      <button
        type="button"
        onClick={onDelete}
        disabled={isBusy}
        className="flex items-center gap-2 rounded-md border border-red-500/30 px-3 py-1.5 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <FiTrash2 size={14} /> Delete
      </button>
    </div>
  )
}

export default ResumeActionBar