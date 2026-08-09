const TimerDisplay = ({ label, value }) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-4 text-center shadow-sm">
    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">{label}</p>
    <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
  </div>
)

export default TimerDisplay
