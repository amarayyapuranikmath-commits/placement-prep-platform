import {
  CheckCircle2,
  XCircle,
  Sparkles,
  ArrowRight,
} from "lucide-react";

const STATUS_LABELS = {
  accepted: "Accepted",
  wrong_answer: "Wrong Answer",
  compile_error: "Compilation Error",
  runtime_error: "Runtime Error",
};

const hasTextValue = (value) =>
  typeof value === "string" && value.trim().length > 0;

const hasFeedbackContent = (feedback) => {
  if (!feedback || typeof feedback !== "object") {
    return false;
  }

  const textFields = [
    "correctness",
    "algorithm_used",
    "explanation",
    "time_complexity",
    "space_complexity",
    "code_quality",
    "overall_rating",
  ];

  const listFields = [
    "suggestions",
    "optimization_suggestions",
    "edge_cases_missed",
    "relevant_edge_cases",
    "interview_tips",
  ];

  return (
    textFields.some((field) => hasTextValue(feedback[field])) ||
    listFields.some((field) => Array.isArray(feedback[field]) && feedback[field].length > 0)
  );
};

const renderTextOrPlaceholder = (value) =>
  hasTextValue(value) ? value : "—";

const SubmissionResultPanel = ({
  submitResult,
  submitError,
  onNextProblem,
}) => {
  if (submitError) {
    return (
      <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-5">
        <p className="text-sm text-red-400">
          {submitError}
        </p>
      </div>
    );
  }

  if (!submitResult) {
    return null;
  }

  const isAccepted =
    submitResult.status === "accepted";

  const hasAiFeedback = hasFeedbackContent(submitResult.ai_feedback);

  return (
    <div
      className={`rounded-3xl border p-5 ${
        isAccepted
          ? "border-emerald-500/20 bg-emerald-500/5"
          : "border-red-500/20 bg-red-500/5"
      }`}
    >
      {/* Status */}

      <div className="flex items-center gap-3">

        {isAccepted ? (
          <CheckCircle2
            size={22}
            className="text-emerald-400"
          />
        ) : (
          <XCircle
            size={22}
            className="text-red-400"
          />
        )}

        <div>

          <p
            className={`text-base font-semibold ${
              isAccepted
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {STATUS_LABELS[submitResult.status] ??
              submitResult.status}
          </p>

          {(submitResult.runtime_ms != null ||
            submitResult.memory_kb != null ||
            submitResult.passed_test_cases != null) && (
            <p className="text-xs text-slate-500">

              {submitResult.runtime_ms != null && (
                <>
                  Runtime: {Math.round(submitResult.runtime_ms)} ms
                </>
              )}

              {submitResult.memory_kb != null && (
                <>
                  {submitResult.runtime_ms != null ? " · " : ""}
                  Memory: {(submitResult.memory_kb / 1024).toFixed(2)} MB
                </>
              )}

              {submitResult.passed_test_cases != null && (
                <>
                  {(submitResult.runtime_ms != null || submitResult.memory_kb != null) ? " · " : ""}
                  Passed: {submitResult.passed_test_cases}/{submitResult.total_test_cases}
                </>
              )}

            </p>
          )}
          {submitResult.failure_reason && submitResult.status !== "accepted" && (
            <p className="mt-2 text-xs text-slate-400">
              {submitResult.failure_reason}
            </p>
          )}

        </div>

      </div>

      {/* Compile Error */}

      {submitResult.compile_error && (
        <pre className="mt-4 overflow-x-auto whitespace-pre-wrap rounded-xl bg-slate-950 p-4 font-mono text-xs text-red-300">
          {submitResult.compile_error}
        </pre>
      )}

      {/* AI Feedback */}

      {hasAiFeedback && (
        <div className="mt-5 border-t border-slate-800 pt-5">

          <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-accent">
            <Sparkles size={14} />
            AI Feedback
          </div>

          {submitResult.ai_feedback.correctness && (
            <div className="mb-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Correctness</p>
              <p className="mt-1">{submitResult.ai_feedback.correctness}</p>
            </div>
          )}

          {submitResult.ai_feedback.algorithm_used && (
            <div className="mb-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Algorithm Used</p>
              <p className="mt-1">{submitResult.ai_feedback.algorithm_used}</p>
            </div>
          )}

          {submitResult.ai_feedback.explanation && (
            <p className="text-sm leading-6 text-slate-300">
              {submitResult.ai_feedback.explanation}
            </p>
          )}

          {(submitResult.ai_feedback.time_complexity ||
            submitResult.ai_feedback.space_complexity) && (
            <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-400">

              {submitResult.ai_feedback.time_complexity && (
                <span>
                  <span className="font-medium text-slate-200">Time Complexity:</span>{" "}
                  {submitResult.ai_feedback.time_complexity}
                </span>
              )}

              {submitResult.ai_feedback.space_complexity && (
                <span>
                  <span className="font-medium text-slate-200">Space Complexity:</span>{" "}
                  {submitResult.ai_feedback.space_complexity}
                </span>
              )}

            </div>
          )}

          {submitResult.ai_feedback.code_quality && (
            <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Code Quality</p>
              <p className="mt-1">{submitResult.ai_feedback.code_quality}</p>
            </div>
          )}

          {submitResult.ai_feedback.overall_rating && (
            <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Overall Rating</p>
              <p className="mt-1 font-medium text-slate-100">{submitResult.ai_feedback.overall_rating}</p>
            </div>
          )}

          {(submitResult.ai_feedback.optimization_suggestions?.length > 0 ||
            submitResult.ai_feedback.suggestions?.length > 0) && (
            <div className="mt-4">
              <p className="text-sm font-medium text-slate-200">Optimization Suggestions</p>
              <ul className="mt-2 space-y-2">
                {(submitResult.ai_feedback.optimization_suggestions?.length > 0
                  ? submitResult.ai_feedback.optimization_suggestions
                  : submitResult.ai_feedback.suggestions)
                  .map((suggestion, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-2 text-sm text-slate-400"
                    >
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-600" />

                      <span>{suggestion}</span>
                    </li>
                  ))}
              </ul>
            </div>
          )}

          {submitResult.ai_feedback.relevant_edge_cases?.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-slate-200">Relevant Edge Cases</p>
              <ul className="mt-2 space-y-2">
                {submitResult.ai_feedback.relevant_edge_cases.map((edgeCase, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-slate-400">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-600" />
                    <span>{edgeCase}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {submitResult.ai_feedback.interview_tips?.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-slate-200">Interview Tips</p>
              <ul className="mt-2 space-y-2">
                {submitResult.ai_feedback.interview_tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-slate-400">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-600" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {submitResult.ai_feedback.edge_cases_missed?.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-slate-200">Edge cases missed</p>
              <ul className="mt-2 space-y-2">
                {submitResult.ai_feedback.edge_cases_missed.map((edgeCase, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm text-slate-400"
                  >
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-600" />
                    <span>{edgeCase}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>
      )}

      {/* Next Problem */}

      {isAccepted && onNextProblem && (
        <button
          type="button"
          onClick={onNextProblem}
          className="mt-5 flex items-center gap-2 rounded-xl bg-accent px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Next Problem

          <ArrowRight size={15} />
        </button>
      )}
    </div>
  );
};

export default SubmissionResultPanel;