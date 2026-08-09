const OptionCard = ({ value, isSelected, onSelect }) => (
  <button
    type="button"
    onClick={() => onSelect(value)}
    className={`w-full rounded-3xl border px-4 py-4 text-left transition-colors focus:outline-none sm:px-5 sm:py-4 ${
      isSelected
        ? 'border-accent bg-accent/10 text-white shadow-accent/10'
        : 'border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-600 hover:bg-slate-900/90'
    }`}
  >
    <span className="text-sm font-medium">{value}</span>
  </button>
)

export default OptionCard
