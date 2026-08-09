import { CheckCircle2, XCircle } from "lucide-react";

const ConsolePanel = ({ runResult, runError, isRunning }) => {
  if (isRunning) {
    return (
      <div className="flex items-center justify-center rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <p className="text-sm text-slate-500">
          Running visible test cases...
        </p>
      </div>
    );
  }

  if (runError) {
    return (
      <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-4">
        <p className="text-sm text-red-400">{runError}</p>
      </div>
    );
  }

  if (!runResult) {
    return (
      <div className="rounded-3xl border border-dashed border-slate-800 p-6 text-center">
        <p className="text-sm text-slate-600">
          Run your code to see the output here.
        </p>
      </div>
    );
  }

  if (runResult.compile_error) {
    return (
      <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-400">
          Compilation Error
        </p>

        <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 font-mono text-xs text-red-300">
          {runResult.compile_error}
        </pre>
      </div>
    );
  }

  if (!runResult.results?.length) {
    return (
      <div className="rounded-3xl border border-slate-800 p-6 text-center">
        <p className="text-sm text-slate-500">
          No test case results available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className={`rounded-2xl border px-4 py-3 text-sm ${runResult.all_passed ? "border-emerald-500/20 bg-emerald-500/5 text-emerald-400" : "border-slate-800 bg-slate-950/70 text-slate-300"}`}>
        {runResult.all_passed ? "All visible test cases passed." : "Some visible test cases need attention."}
      </div>

      {runResult.results.map((result, index) => (
        <div
          key={result.id ?? result.test_case_id ?? index}
          className={`rounded-2xl border p-4 ${
            result.passed
              ? "border-emerald-500/20 bg-emerald-500/5"
              : "border-red-500/20 bg-red-500/5"
          }`}
        >
          <div className="mb-3 flex items-center gap-2">
            {result.passed ? (
              <CheckCircle2
                size={16}
                className="text-emerald-400"
              />
            ) : (
              <XCircle
                size={16}
                className="text-red-400"
              />
            )}

            <span className="text-xs font-medium text-slate-300">
              Test Case {index + 1}
            </span>

            <div className="ml-auto flex flex-wrap items-center gap-3 text-xs text-slate-500">
              {result.runtime_ms != null && (
                <span>{Math.round(result.runtime_ms)} ms</span>
              )}
              {result.memory_kb != null && (
                <span>{(result.memory_kb / 1024).toFixed(2)} MB</span>
              )}
            </div>
          </div>

          <div className="space-y-3 text-xs">

            <div>
              <p className="mb-1 text-slate-500">
                Input
              </p>

              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 font-mono text-slate-300">
                {result.input || "—"}
              </pre>
            </div>

            <div>
              <p className="mb-1 text-slate-500">
                Expected Output
              </p>

              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 font-mono text-slate-300">
                {result.expected_output || "—"}
              </pre>
            </div>

            <div>
              <p className="mb-1 text-slate-500">
                Your Output
              </p>

              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 font-mono text-slate-300">
                {result.actual_output ?? "—"}
              </pre>
            </div>

            {result.stderr && (
              <div>
                <p className="mb-1 text-red-400">
                  Runtime Error
                </p>

                <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 font-mono text-red-300">
                  {result.stderr}
                </pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ConsolePanel;