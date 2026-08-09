const ResultCard = ({ label, value, note }) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm">
    <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{label}</p>
    <p className="mt-4 text-3xl font-semibold text-white">{value}</p>
    {note && <p className="mt-2 text-sm text-slate-400">{note}</p>}
  </div>
)

export default ResultCard
