import LoadingSpinner from './LoadingSpinner'

export default function PageLoader({ label = 'Loading experience...' }) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 text-center shadow-glass">
        <div className="mb-4 flex justify-center">
          <LoadingSpinner />
        </div>
        <p className="text-sm font-semibold text-slate-100">{label}</p>
        <p className="mt-2 text-sm text-slate-400">Preparing the next page for you.</p>
      </div>
    </div>
  )
}
