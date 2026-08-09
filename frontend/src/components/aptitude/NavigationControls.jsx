const NavigationControls = ({ onPrevious, onNext, onMark, onClear, onSubmit, disablePrevious, disableNext }) => (
  <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
    <div className="grid gap-3 sm:grid-cols-3">
      <button
        type="button"
        onClick={onPrevious}
        disabled={disablePrevious}
        className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Previous
      </button>
      <button
        type="button"
        onClick={onNext}
        disabled={disableNext}
        className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Next
      </button>
      <button
        type="button"
        onClick={onMark}
        className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90"
      >
        Mark for Review
      </button>
    </div>
    <div className="grid gap-3 sm:grid-cols-2">
      <button
        type="button"
        onClick={onClear}
        className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90"
      >
        Clear Answer
      </button>
      <button
        type="button"
        onClick={onSubmit}
        className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
      >
        Submit Test
      </button>
    </div>
  </div>
)

export default NavigationControls
