const ConfigurationForm = ({ config, onChange, onSubmit }) => (
  <div className="mx-auto max-w-2xl rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm sm:p-8">
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Setup</p>
        <h2 className="mt-3 text-2xl font-semibold text-white">Test configuration</h2>
        <p className="mt-2 text-sm text-slate-400">Choose a focused module, difficulty, and duration that fits your practice session.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <label className="space-y-2 text-sm text-slate-200">
          <span className="block font-medium">Test Type</span>
          <select
            value={config.testType}
            onChange={(event) => onChange('testType', event.target.value)}
            className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          >
            <option>Quantitative Aptitude</option>
            <option>Logical Reasoning</option>
            <option>Verbal Ability</option>
            <option>Data Interpretation</option>
            <option>Mixed Aptitude</option>
          </select>
        </label>

        <label className="space-y-2 text-sm text-slate-200">
          <span className="block font-medium">Difficulty</span>
          <select
            value={config.difficulty}
            onChange={(event) => onChange('difficulty', event.target.value)}
            className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          >
            <option>Easy</option>
            <option>Medium</option>
            <option>Hard</option>
          </select>
        </label>

        <label className="space-y-2 text-sm text-slate-200">
          <span className="block font-medium">Number of Questions</span>
          <select
            value={config.questionCount}
            onChange={(event) => onChange('questionCount', Number(event.target.value))}
            className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={30}>30</option>
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={onSubmit}
        className="w-full rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
      >
        Start Test
      </button>
    </div>
  </div>
)

export default ConfigurationForm
