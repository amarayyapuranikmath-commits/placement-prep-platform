import React from 'react'

const ProblemStatementPanel = ({ problem }) => {
  if (!problem) return null

  return (
    <section className="space-y-4 rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-glow">
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white">Problem Statement</h2>
            <p className="text-sm text-slate-400">{problem.category} · {problem.difficulty}</p>
          </div>
        </div>

        <div className="space-y-4 text-slate-200">
          <p>{problem.statement}</p>

          {problem.input_format && (
            <div>
              <h3 className="text-sm font-semibold text-white">Input Format</h3>
              <p className="mt-2 text-sm text-slate-300">{problem.input_format}</p>
            </div>
          )}

          {problem.output_format && (
            <div>
              <h3 className="text-sm font-semibold text-white">Output Format</h3>
              <p className="mt-2 text-sm text-slate-300">{problem.output_format}</p>
            </div>
          )}

          {problem.constraints && (
            <div>
              <h3 className="text-sm font-semibold text-white">Constraints</h3>
              <p className="mt-2 text-sm text-slate-300">{problem.constraints}</p>
            </div>
          )}

          {Array.isArray(problem.examples) && problem.examples.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-white">Examples</h3>
              <div className="mt-3 space-y-4">
                {problem.examples.map((example, index) => (
                  <div key={index} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
                    <p className="text-sm font-semibold text-slate-200">Example {index + 1}</p>
                    <div className="mt-2 space-y-2 text-sm text-slate-300">
                      <div>
                        <span className="font-medium text-slate-100">Input:</span>
                        <pre className="mt-1 overflow-x-auto rounded bg-slate-950/80 p-3 text-xs leading-relaxed text-slate-200">{example.input}</pre>
                      </div>
                      <div>
                        <span className="font-medium text-slate-100">Output:</span>
                        <pre className="mt-1 overflow-x-auto rounded bg-slate-950/80 p-3 text-xs leading-relaxed text-slate-200">{example.expected_output}</pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default ProblemStatementPanel
