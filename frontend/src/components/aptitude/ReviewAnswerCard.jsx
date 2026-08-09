const ReviewAnswerCard = ({ question, selectedAnswer, correctAnswer, explanation, isCorrect }) => (
  <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm sm:p-8">
    <div className="space-y-4">
      <div className="flex items-center gap-3 text-sm text-slate-400">
        <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.3em] ${
          isCorrect ? 'bg-emerald-500/10 text-emerald-300' : 'bg-rose-500/10 text-rose-300'
        }`}>
          {isCorrect ? 'Correct' : 'Incorrect'}
        </span>
        <span>{isCorrect ? 'Great work' : 'Review the correct answer below'}</span>
      </div>

      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Question</p>
        <h2 className="mt-2 text-xl font-semibold text-white">{question.question}</h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          <p className="font-medium text-slate-100">Selected Answer</p>
          <p className="mt-2">{selectedAnswer || 'No answer selected'}</p>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          <p className="font-medium text-slate-100">Correct Answer</p>
          <p className="mt-2">{correctAnswer}</p>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
        <p className="font-medium text-slate-100">Explanation</p>
        <p className="mt-2 text-slate-400">{explanation}</p>
      </div>
    </div>
  </section>
)

export default ReviewAnswerCard
