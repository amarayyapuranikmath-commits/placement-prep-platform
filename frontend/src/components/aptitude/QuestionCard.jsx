import OptionCard from './OptionCard'

const QuestionCard = ({ question, selectedAnswer, onSelectAnswer }) => (
  <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm sm:p-8">
    <div className="space-y-4">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Question</p>
        <h2 className="mt-3 text-xl font-semibold text-white">{question.question}</h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {question.options.map((option) => (
          <OptionCard
            key={option}
            value={option}
            isSelected={selectedAnswer === option}
            onSelect={onSelectAnswer}
          />
        ))}
      </div>
    </div>
  </section>
)

export default QuestionCard
