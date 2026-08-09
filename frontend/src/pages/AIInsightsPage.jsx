import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Sparkles, ArrowRight, Check, CircleDot, AlertTriangle, ShieldCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import AIInsightsSummaryCard from '../components/aiInsights/AIInsightsSummaryCard'
import AIInsightsChatInput from '../components/aiInsights/AIInsightsChatInput'
import AIInsightsPanel from '../components/aiInsights/AIInsightsPanel'
import { getInsights, askInsightQuestion } from '../services/insightsService'

const DEFAULT_RECOMMENDATIONS = [
  {
    title: 'Practice Coding',
    description: 'Sharpen your algorithms and build consistency with targeted problems.',
    route: '/coding',
  },
  {
    title: 'Start AI Interview',
    description: 'Practice interview conversations and refine your responses.',
    route: '/interview',
  },
  {
    title: 'Take Aptitude Test',
    description: 'Improve your speed and accuracy before the next challenge.',
    route: '/aptitude',
  },
  {
    title: 'Improve Resume',
    description: 'Polish your resume to match recruiter expectations.',
    route: '/resume',
  },
]

const formatDate = (value) => {
  if (!value) return null

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

const normalizeTextArray = (value) => {
  if (!value) return []
  if (typeof value === 'string') return value.split(/\n|\.|;/).map((item) => item.trim()).filter(Boolean)
  if (Array.isArray(value)) return value.map((item) => (typeof item === 'string' ? item.trim() : item?.title || item?.name || '')).filter(Boolean)
  return []
}

const normalizeRecommendations = (value) => {
  if (!value) return DEFAULT_RECOMMENDATIONS
  if (Array.isArray(value)) {
    return value.map((item, index) => {
      if (typeof item === 'string') {
        return {
          title: item,
          description: '',
          route: DEFAULT_RECOMMENDATIONS[index]?.route || '/coding',
        }
      }
      return {
        title: item.title || item.name || 'Next step',
        description: item.description || item.summary || '',
        route: item.route || item.path || DEFAULT_RECOMMENDATIONS[index]?.route || '/coding',
      }
    })
  }
  return DEFAULT_RECOMMENDATIONS
}

const normalizeInsights = (data = {}) => {
  const rawSummary = data.summary || {}
  const getSummaryText = (key, fallbackKeys = []) => {
    const rawValue = rawSummary[key] ?? data[key]
    if (typeof rawValue === 'string') return rawValue
    if (rawValue?.content) return rawValue.content
    for (const fallbackKey of fallbackKeys) {
      const fallback = rawSummary[fallbackKey] ?? data[fallbackKey]
      if (typeof fallback === 'string') return fallback
      if (fallback?.content) return fallback.content
    }
    return null
  }

  const summary = {
    overview: getSummaryText('overview', ['description', 'insight', 'summary']),
    progress: getSummaryText('progress', ['current_progress', 'status']),
    strengths: getSummaryText('strengths', ['what_you_are_doing_well', 'strengths_summary']),
    weaknesses: getSummaryText('weaknesses', ['what_needs_attention', 'weaknesses_summary']),
    observation: getSummaryText('observation', ['overall_observation', 'final_note']),
  }

  return {
    lastUpdated: data.last_updated || data.updated_at || data.generated_at || null,
    summary,
    strengths: normalizeTextArray(data.strengths || data.top_strengths || data.strong_points),
    improvementAreas: normalizeTextArray(data.areas_to_improve || data.improvements || data.weaknesses),
    recommendations: normalizeRecommendations(data.recommendations || data.next_steps),
  }
}

const FeatureList = ({ items, icon: Icon, emptyLabel }) => (
  <div className="space-y-3">
    <div className="flex items-center gap-3 text-slate-400">
      <Icon size={16} />
      <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500">{emptyLabel || 'Key points'}</p>
    </div>
    <div className="space-y-2">
      {items.length > 0 ? (
        items.map((item, index) => (
          <div key={`${item}-${index}`} className="flex items-start gap-3 rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3">
            <span className="mt-1 inline-flex h-7 w-7 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
              <Check size={14} />
            </span>
            <p className="text-sm text-slate-300">{item}</p>
          </div>
        ))
      ) : (
        <p className="rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-500">
          No insights available yet.
        </p>
      )}
    </div>
  </div>
)

const AIInsightsPage = () => {
  const navigate = useNavigate()
  const [insights, setInsights] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [isQueryLoading, setIsQueryLoading] = useState(false)

  const loadInsights = async () => {
    setIsLoading(true)
    setError('')
    try {
      const rawData = await getInsights()
      setInsights(normalizeInsights(rawData))
    } catch (err) {
      setError(err?.response?.data?.message || err.message || 'Unable to generate AI insights.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadInsights()
  }, [])

  const handleQuerySubmit = async () => {
    if (!question.trim()) return
    setIsQueryLoading(true)
    setResponse('')

    try {
      const result = await askInsightQuestion(question.trim())
      const answer = result?.answer || result?.response || result?.text || result?.message || 'The AI did not return an answer.'
      setResponse(answer)
    } catch (err) {
      setResponse(err?.response?.data?.message || err.message || 'Unable to get a response right now.')
    } finally {
      setIsQueryLoading(false)
    }
  }

  const handleSuggestionClick = (prompt) => {
    setQuestion(prompt)
  }

  const hasContent = !!insights && (!!insights.summary.overview || insights.strengths.length > 0 || insights.improvementAreas.length > 0)

  return (
    <div className="mx-auto max-w-7xl px-4 pb-10 pt-2 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-3 rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass backdrop-blur-xl sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.32em] text-slate-500">AI Insights</p>
          <h1 className="max-w-2xl text-3xl font-semibold text-slate-100 sm:text-4xl">
            Personalized analysis of your placement preparation.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-400">
            Understand your strengths, focus on the most valuable next steps, and ask the AI for real-time guidance.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:items-end">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 px-4 py-3 text-sm text-slate-400">
            Last updated
            <div className="mt-1 font-medium text-slate-100">
              {formatDate(insights?.lastUpdated) || 'Not available'}
            </div>
          </div>
          <button
            type="button"
            onClick={loadInsights}
            disabled={isLoading}
            className="inline-flex items-center justify-center rounded-2xl bg-violet-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw size={16} className="mr-2" />
            Refresh Analysis
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-8 shadow-glass"
          >
            <div className="animate-pulse space-y-6">
              <div className="h-6 w-48 rounded-full bg-slate-800" />
              <div className="h-5 w-3/4 rounded-full bg-slate-800" />
              <div className="grid gap-4 lg:grid-cols-[1.5fr_0.9fr]">
                <div className="space-y-4 rounded-[28px] bg-slate-900/80 p-6">
                  <div className="h-4 w-24 rounded-full bg-slate-800" />
                  <div className="h-3 rounded-full bg-slate-800" />
                  <div className="h-3 rounded-full bg-slate-800" />
                  <div className="h-3 rounded-full bg-slate-800" />
                </div>
                <div className="space-y-4 rounded-[28px] bg-slate-900/80 p-6">
                  <div className="h-4 w-32 rounded-full bg-slate-800" />
                  <div className="h-3 rounded-full bg-slate-800" />
                  <div className="h-3 rounded-full bg-slate-800" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      ) : error ? (
        <ErrorMessage message={error} onRetry={loadInsights} />
      ) : !hasContent ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-10 text-center shadow-glass"
        >
          <Sparkles size={28} className="mx-auto mb-4 text-violet-300" />
          <h2 className="text-2xl font-semibold text-slate-100">No AI insights available yet.</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-400">
            Complete interviews, coding practice, aptitude tests, or resume analysis to generate personalized insights.
          </p>
          <button
            type="button"
            onClick={loadInsights}
            className="mt-8 inline-flex items-center justify-center rounded-2xl bg-violet-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-violet-400"
          >
            Generate Insights
          </button>
        </motion.div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.85fr]">
          <div className="space-y-6">
            <AIInsightsSummaryCard
              summary={{
                overview: insights.summary.overview && { title: 'Overview', content: insights.summary.overview },
                progress: insights.summary.progress && { title: 'Current Progress', content: insights.summary.progress },
                strengths: insights.summary.strengths && { title: "What You're Doing Well", content: insights.summary.strengths },
                weaknesses: insights.summary.weaknesses && { title: 'What Needs Attention', content: insights.summary.weaknesses },
                observation: insights.summary.observation && { title: 'Overall Observation', content: insights.summary.observation },
              }}
            />

            <AIInsightsPanel
              title="AI Insights"
              description="Ask anything about your preparation."
              actionText="Learn more"
              actionHref="#ask-ai"
              withBorder
            >
              <p className="text-sm leading-7 text-slate-400">
                Use the AI assistant to deep dive into your preparation, uncover focus areas, and get next-step clarity anytime.
              </p>
            </AIInsightsPanel>

            <div className="space-y-6" id="ask-ai">
              <AIInsightsChatInput
                value={question}
                onChange={setQuestion}
                onSubmit={handleQuerySubmit}
                onSelectPrompt={handleSuggestionClick}
                isLoading={isQueryLoading}
              />

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass"
              >
                <div className="flex items-center gap-3 text-slate-400">
                  <CircleDot size={16} />
                  <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500">AI response</p>
                </div>
                <div className="mt-5 min-h-[6rem] rounded-3xl bg-slate-900/80 p-5 text-sm leading-7 text-slate-300">
                  {isQueryLoading ? (
                    <div className="flex items-center gap-3 text-slate-400">
                      <LoadingSpinner />
                      Processing your question…
                    </div>
                  ) : response ? (
                    <p>{response}</p>
                  ) : (
                    <p className="text-slate-500">Ask a question to receive concise, tailored guidance from the AI.</p>
                  )}
                </div>
              </motion.div>
            </div>
          </div>

          <aside className="space-y-6">
            <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-100">Strengths</p>
                  <p className="mt-1 text-sm text-slate-500">Top areas where you are already performing well.</p>
                </div>
                <ShieldCheck size={20} className="text-violet-300" />
              </div>
              <div className="mt-5 space-y-3">
                {insights.strengths.length > 0 ? (
                  insights.strengths.slice(0, 4).map((item, index) => (
                    <div key={index} className="flex items-center gap-3 rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300">
                      <span className="inline-flex h-8 w-8 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">✓</span>
                      <span>{item}</span>
                    </div>
                  ))
                ) : (
                  <p className="rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-500">
                    No strengths are available yet.
                  </p>
                )}
              </div>
            </div>

            <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-100">Areas to Improve</p>
                  <p className="mt-1 text-sm text-slate-500">Focus on these key opportunities.</p>
                </div>
                <AlertTriangle size={20} className="text-violet-300" />
              </div>
              <div className="mt-5 space-y-3">
                {insights.improvementAreas.length > 0 ? (
                  insights.improvementAreas.slice(0, 5).map((item, index) => (
                    <div key={index} className="rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300">
                      • {item}
                    </div>
                  ))
                ) : (
                  <p className="rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-500">
                    No improvement areas are available yet.
                  </p>
                )}
              </div>
            </div>

            <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-6 shadow-glass">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-100">Recommended Next Steps</p>
                  <p className="mt-1 text-sm text-slate-500">A small set of actions to move forward.</p>
                </div>
                <Sparkles size={20} className="text-violet-300" />
              </div>
              <div className="mt-5 space-y-4">
                {insights.recommendations.slice(0, 5).map((item, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => navigate(item.route)}
                    className="w-full rounded-3xl border border-slate-800 bg-slate-900/70 px-4 py-4 text-left transition hover:border-violet-500/40 hover:bg-slate-900"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-100">{item.title}</p>
                        <p className="mt-1 text-sm text-slate-500">{item.description}</p>
                      </div>
                      <ArrowRight size={18} className="text-violet-300" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}

export default AIInsightsPage
