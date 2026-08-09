import DifficultyBadge from './DifficultyBadge'

const ProblemListTable = ({ problems, page, totalPages, isLoading = false, onPageChange, onSelectProblem }) => {
  if (isLoading) {
    return (
      <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/80 shadow-glass backdrop-blur-xl">
        <div className="grid grid-cols-4 gap-0 border-b border-slate-800 bg-slate-950/90 px-5 py-4 text-xs uppercase tracking-[0.08em] text-slate-500">
          <div className="font-semibold">Problem Name</div>
          <div className="font-semibold">Difficulty</div>
          <div className="font-semibold">Acceptance</div>
          <div className="font-semibold">Status</div>
        </div>

        <div className="divide-y divide-slate-800">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="grid grid-cols-4 gap-0 px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-slate-700" />
                <div className="h-4 w-40 animate-pulse rounded bg-slate-800" />
              </div>
              <div className="h-6 w-20 animate-pulse rounded bg-slate-800" />
              <div className="h-4 w-16 animate-pulse rounded bg-slate-800" />
              <div className="h-4 w-16 animate-pulse rounded bg-slate-800" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (problems.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-10 text-center">
        <p className="text-sm font-medium text-slate-100">No problems match your filters.</p>
        <p className="mt-2 text-sm text-slate-500">Try widening the search or clearing a filter to see more challenges.</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/80 shadow-glass backdrop-blur-xl">
      <div className="grid grid-cols-4 gap-0 border-b border-slate-800 bg-slate-950/90 px-5 py-4 text-xs uppercase tracking-[0.08em] text-slate-500">
        <div className="font-semibold">Problem Name</div>
        <div className="font-semibold">Difficulty</div>
        <div className="font-semibold">Acceptance</div>
        <div className="font-semibold">Status</div>
      </div>

      <div className="divide-y divide-slate-800">
        {problems.map((problem) => (
          <button
            key={problem.id}
            type="button"
            onClick={() => onSelectProblem(problem.id)}
            className="grid grid-cols-4 gap-0 px-5 py-4 text-left transition-colors hover:bg-slate-950"
          >
            <div className="flex items-center gap-3">
              <span className={`h-2.5 w-2.5 rounded-full ${problem.is_solved ? 'bg-emerald-400' : 'bg-slate-600'}`} />
              <span className="text-sm font-medium text-slate-100">{problem.title}</span>
            </div>

            <div>
              <DifficultyBadge difficulty={problem.difficulty} />
            </div>

            <div className="text-sm text-slate-300">
              {typeof problem.acceptance_rate === 'number'
                ? `${Math.round(problem.acceptance_rate * 100)}%`
                : 'N/A'}
            </div>

            <div className={`text-sm font-medium ${problem.is_solved ? 'text-emerald-400' : 'text-slate-400'}`}>
              {problem.is_solved ? 'Solved' : 'Unsolved'}
            </div>
          </button>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-800 px-5 py-3">
          <button
            type="button"
            onClick={() => onPageChange(Math.max(page - 1, 1))}
            disabled={page <= 1}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-slate-400 transition-colors hover:bg-slate-800 hover:text-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-xs text-slate-500">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => onPageChange(Math.min(page + 1, totalPages))}
            disabled={page >= totalPages}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-slate-400 transition-colors hover:bg-slate-800 hover:text-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default ProblemListTable