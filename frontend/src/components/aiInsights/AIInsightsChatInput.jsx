import { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'

const prompts = [
  'What should I study next?',
  'Explain my interview mistakes.',
  'Create a weekly study plan.',
  'Why is my aptitude score low?',
]

const AIInsightsChatInput = ({ value, onChange, onSubmit, onSelectPrompt, isLoading }) => {
  const [focused, setFocused] = useState(false)

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-4 shadow-glass transition-all duration-300">
      <div className="flex items-center gap-3 text-slate-400">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-800 text-violet-300">
          <Sparkles size={18} />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-100">Ask the AI</p>
          <p className="text-xs text-slate-500">Get tailored guidance for your preparation.</p>
        </div>
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault()
          if (value?.trim()) onSubmit()
        }}
        className="mt-4 space-y-4"
      >
        <label className="sr-only" htmlFor="ai-insights-question">
          Ask anything about your preparation
        </label>
        <div
          className={`rounded-3xl border px-4 py-3 transition ${
            focused ? 'border-violet-400/40 bg-slate-950' : 'border-slate-800 bg-slate-900/90'
          }`}
        >
          <input
            id="ai-insights-question"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask anything about your preparation..."
            className="w-full bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-500"
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {prompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => onSelectPrompt(prompt)}
                className="rounded-2xl border border-slate-800 bg-slate-950/80 px-3 py-2 text-left text-sm text-slate-300 transition hover:border-violet-500/40 hover:text-slate-100"
              >
                {prompt}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={!value?.trim() || isLoading}
            className="inline-flex h-11 items-center justify-center rounded-2xl bg-violet-500 px-5 text-sm font-semibold text-slate-950 transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? 'Working...' : 'Send'}
            <Send size={16} className="ml-2" />
          </button>
        </div>
      </form>
    </div>
  )
}

export default AIInsightsChatInput
