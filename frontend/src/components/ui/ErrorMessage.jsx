// src/components/ui/ErrorMessage.jsx
import { FiAlertTriangle } from 'react-icons/fi'

const ErrorMessage = ({ message = 'Something went wrong.', onRetry }) => {
  return (
    <div className="flex flex-col items-center gap-3 rounded-3xl border border-red-500/20 bg-red-500/5 px-6 py-10 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-red-500/10 text-red-400">
        <FiAlertTriangle size={20} />
      </span>
      <p className="max-w-sm text-sm text-slate-300">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition-colors hover:border-accent/50 hover:text-accent"
        >
          Try again
        </button>
      )}
    </div>
  )
}

export default ErrorMessage