const LoadingSkeleton = () => (
  <div className="space-y-4">
    <div className="h-6 w-1/3 rounded-full bg-slate-800" />
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="h-40 rounded-3xl bg-slate-800" />
      <div className="h-40 rounded-3xl bg-slate-800" />
    </div>
    <div className="grid gap-4 sm:grid-cols-3">
      <div className="h-20 rounded-3xl bg-slate-800" />
      <div className="h-20 rounded-3xl bg-slate-800" />
      <div className="h-20 rounded-3xl bg-slate-800" />
    </div>
  </div>
)

export default LoadingSkeleton
