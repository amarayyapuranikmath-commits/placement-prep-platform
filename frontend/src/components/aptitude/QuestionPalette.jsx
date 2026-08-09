const PALETTE_STATUS = {
  answered: 'Answered',
  unanswered: 'Unanswered',
  review: 'Marked for Review',
}

const QuestionPalette = ({ items, currentIndex, onSelect }) => (
  <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm">
    <div className="mb-5 flex items-center justify-between">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Question Palette</p>
        <h2 className="mt-2 text-lg font-semibold text-white">Status overview</h2>
      </div>
      <span className="rounded-full bg-slate-900 px-3 py-1 text-xs text-slate-400">{items.length} total</span>
    </div>

    <div className="grid gap-3 sm:grid-cols-3">
      {items.map((item, index) => (
        <button
          key={item.id}
          type="button"
          onClick={() => onSelect(index)}
          className={`rounded-2xl border px-3 py-3 text-left text-sm transition ${
            index === currentIndex
              ? 'border-accent bg-accent/10 text-white'
              : item.status === 'answered'
              ? 'border-slate-700 bg-slate-900 text-slate-200'
              : item.status === 'review'
              ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-200'
              : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-600 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between gap-2">
            <span className="font-medium truncate">Q{index + 1}</span>
            <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.25em] text-slate-400">
              {PALETTE_STATUS[item.status]}
            </span>
          </div>
        </button>
      ))}
    </div>
  </section>
)

export default QuestionPalette
