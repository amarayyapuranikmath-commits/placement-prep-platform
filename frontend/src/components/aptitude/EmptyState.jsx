const EmptyState = ({ title, subtitle, actionLabel, onAction }) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-8 text-center shadow-sm">
    <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{title}</p>
    <p className="mt-4 text-xl font-semibold text-white">{subtitle}</p>
    {actionLabel && (
      <button
        type="button"
        onClick={onAction}
        className="mt-6 inline-flex rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
      >
        {actionLabel}
      </button>
    )}
  </div>
)

export default EmptyState
