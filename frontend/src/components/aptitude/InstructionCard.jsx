const InstructionCard = ({ title, description, items }) => (
  <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm sm:p-8">
    <div className="space-y-2">
      <h2 className="text-xl font-semibold text-white">{title}</h2>
      <p className="text-sm text-slate-400">{description}</p>
    </div>

    <div className="mt-6 space-y-4">
      {items.map((item) => (
        <div key={item.title} className="rounded-2xl bg-slate-900/80 p-4">
          <p className="text-sm font-medium text-slate-200">{item.title}</p>
          <p className="mt-1 text-sm text-slate-400">{item.detail}</p>
        </div>
      ))}
    </div>
  </section>
)

export default InstructionCard
