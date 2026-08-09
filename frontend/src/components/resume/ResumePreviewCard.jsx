import { FiFileText, FiEye, FiDownload, FiRefreshCw } from 'react-icons/fi'

const formatBytes = (bytes) => {
  if (!bytes) return '0 KB'
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(0)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

const formatDate = (isoString) => {
  if (!isoString) return '—'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(isoString))
}

const ResumePreviewCard = ({ resume, onReplaceClick }) => {
  if (!resume) return null

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/80 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <FiFileText size={20} />
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-slate-100">{resume.file_name}</p>
          <p className="mt-0.5 text-xs text-slate-500">
            {formatBytes(resume.file_size_bytes)} · {formatDate(resume.uploaded_at)}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          disabled
          title="Preview is not available yet"
          className="flex items-center gap-1.5 rounded-md border border-slate-800 px-2 py-1 text-xs font-medium text-slate-600"
        >
          <FiEye size={13} /> Preview
        </button>
        <button
          type="button"
          disabled
          title="Download is not available yet"
          className="flex items-center gap-1.5 rounded-md border border-slate-800 px-2 py-1 text-xs font-medium text-slate-600"
        >
          <FiDownload size={13} /> Download
        </button>
        <button
          type="button"
          onClick={onReplaceClick}
          className="flex items-center gap-1.5 rounded-md border border-slate-700 px-2 py-1 text-xs font-medium text-slate-200 transition-colors hover:border-accent/50 hover:text-accent"
        >
          <FiRefreshCw size={13} /> Replace
        </button>
      </div>
    </div>
  )
}

export default ResumePreviewCard