export default function RoadmapPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
        <h2 className="text-2xl font-semibold text-white">Roadmap</h2>
        <p className="mt-2 text-sm text-slate-400">Track your learning path through preparation modules.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-3">
        {['Getting Started', 'Interview Prep', 'Coding Mastery'].map((step) => (
          <div key={step} className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Step</p>
            <h3 className="mt-3 text-xl font-semibold text-white">{step}</h3>
            <p className="mt-2 text-sm text-slate-400">Complete milestone tasks and build confidence for the next stage.</p>
          </div>
        ))}
      </div>
    </div>
  )
}
