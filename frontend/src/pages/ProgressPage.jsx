import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, Brain, Code2, FileText, MessageSquare, User, RefreshCw, Download, History, Loader2, X } from 'lucide-react'
import ProgressChart from '../components/progress/ProgressChart'
import { getProgressOverview, getProgressModules, getProgressAnalytics, getRecentActivity, getProgressModuleHistory, downloadProgressReport } from '../services/progress/progressService'

const TAB_CONFIG = [
  { key: 'interview', label: 'AI Interview', icon: MessageSquare },
  { key: 'aptitude', label: 'Aptitude', icon: Brain },
  { key: 'coding', label: 'Coding', icon: Code2 },
  { key: 'resume', label: 'Resume', icon: FileText },
]

const MODULE_ICON_MAP = {
  interview: MessageSquare,
  aptitude: Brain,
  coding: Code2,
  resume: FileText,
  profile: User,
}

const getInitialState = () => ({
  overall: null,
  modules: [],
  analytics: [],
  activity: [],
  selectedTab: 'interview',
  loading: true,
  error: '',
  reportState: 'idle',
})

export default function ProgressPage() {
  const [state, setState] = useState(getInitialState())
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [analyticsCache, setAnalyticsCache] = useState({})
  const [historyOpen, setHistoryOpen] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyItems, setHistoryItems] = useState([])
  const [historyError, setHistoryError] = useState('')

  const loadData = async () => {
    setState((prev) => ({ ...prev, loading: true, error: '' }))

    try {
      const [overview, modules, analytics, activity] = await Promise.all([
        getProgressOverview(),
        getProgressModules(),
        getProgressAnalytics('interview'),
        getRecentActivity(),
      ])

      const initialAnalytics = analytics?.points ?? []
      setState({
        overall: overview?.overall ?? null,
        modules: modules?.modules ?? [],
        analytics: initialAnalytics,
        activity: activity?.activity ?? [],
        selectedTab: 'interview',
        loading: false,
        error: '',
        reportState: 'idle',
      })
      setAnalyticsCache((prev) => ({ ...prev, interview: initialAnalytics }))
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error?.message || 'Unable to load progress data right now.',
      }))
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleTabChange = async (moduleKey) => {
    setState((prev) => ({ ...prev, selectedTab: moduleKey, error: '' }))

    if (analyticsCache[moduleKey]) {
      setState((prev) => ({ ...prev, analytics: analyticsCache[moduleKey] }))
      return
    }

    setAnalyticsLoading(true)

    try {
      const analytics = await getProgressAnalytics(moduleKey)
      const nextAnalytics = analytics?.points ?? []
      setState((prev) => ({ ...prev, analytics: nextAnalytics }))
      setAnalyticsCache((prev) => ({ ...prev, [moduleKey]: nextAnalytics }))
    } catch (error) {
      setState((prev) => ({ ...prev, error: error?.message || 'Unable to load analytics.' }))
    } finally {
      setAnalyticsLoading(false)
    }
  }

  const handleOpenHistory = async () => {
    setHistoryOpen(true)
    setHistoryLoading(true)
    setHistoryError('')
    setHistoryItems([])

    try {
      const items = await getProgressModuleHistory(state.selectedTab)
      setHistoryItems(items || [])
    } catch (error) {
      setHistoryError(error?.response?.data?.message || error?.message || 'Unable to load history right now.')
    } finally {
      setHistoryLoading(false)
    }
  }

  const handleDownload = async () => {
    setState((prev) => ({ ...prev, reportState: 'loading' }))

    try {
      const response = await downloadProgressReport()
      const blob = response?.data || response
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'placement-progress-report.pdf'
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      setState((prev) => ({ ...prev, reportState: 'success' }))
    } catch (error) {
      setState((prev) => ({ ...prev, reportState: 'error' }))
    }
  }

  const chartMetricLabel = useMemo(() => {
    return TAB_CONFIG.find((tab) => tab.key === state.selectedTab)?.label || 'Analytics'
  }, [state.selectedTab])

  const historyTitle = useMemo(() => {
    return TAB_CONFIG.find((tab) => tab.key === state.selectedTab)?.label || 'Selected module'
  }, [state.selectedTab])

  const selectedModule = useMemo(() => {
    return state.modules.find((module) => module.key === state.selectedTab) || state.modules[0] || null
  }, [state.modules, state.selectedTab])

  const chartStats = useMemo(() => {
    const values = (state.analytics || []).map((item) => Number(item.value) || 0)
    const average = values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : 0
    const best = values.length ? Math.max(...values) : 0
    const latest = values.length ? values[values.length - 1] : 0
    const attempts = selectedModule?.attempts ?? 0

    return [
      { label: 'Average Score', value: `${average}%` },
      { label: 'Best Score', value: `${best}%` },
      { label: 'Latest Result', value: `${latest}%` },
      { label: 'Total Attempts', value: attempts },
    ]
  }, [selectedModule, state.analytics])

  const emptyState = !state.loading && state.modules.length === 0 && !state.error
  const loadingState = state.loading
  const overallProgress = Math.min(100, Math.max(0, Number(state.overall?.percentage ?? 0)))
  const completedModules = state.modules.filter((module) => Number(module.progress) >= 70).length

  const formatHistoryDate = (value) => {
    if (!value) return 'No date available'
    const dateValue = new Date(value)
    if (Number.isNaN(dateValue.getTime())) return 'No date available'
    return dateValue.toLocaleString([], { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
  }

  const getHistorySummary = (item, moduleKey) => {
    if (moduleKey === 'interview') {
      const score = item?.score ?? item?.summary?.score ?? item?.result?.score ?? item?.performance?.score
      const status = item?.status || item?.result?.status || 'Completed'
      return {
        primary: score != null ? `${Number(score)}%` : 'Completed',
        secondary: status,
        detail: item?.summary?.feedback || item?.feedback || item?.notes || 'Interview session completed',
      }
    }

    if (moduleKey === 'aptitude') {
      const score = item?.summary?.score ?? item?.score
      const status = item?.status || 'Completed'
      return {
        primary: score != null ? `${Number(score)}%` : 'Completed',
        secondary: status,
        detail: item?.summary?.feedback || item?.feedback || item?.remarks || 'Aptitude session completed',
      }
    }

    if (moduleKey === 'coding') {
      const status = item?.status || 'Submitted'
      const result = item?.result || item?.summary?.result || item?.message || 'Submission recorded'
      return {
        primary: status,
        secondary: result,
        detail: item?.problem_id ? `Problem ${item.problem_id}` : 'Coding attempt recorded',
      }
    }

    if (moduleKey === 'resume') {
      const score = item?.ats_score ?? item?.summary?.ats_score
      const status = item?.status || 'Analyzed'
      return {
        primary: score != null ? `${Number(score)}% ATS` : 'Analysis completed',
        secondary: status,
        detail: item?.summary?.notes || item?.notes || 'Resume analysis completed',
      }
    }

    return {
      primary: 'Completed',
      secondary: 'Recorded',
      detail: 'History recorded',
    }
  }

  return (
    <div className="space-y-2.5">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/80 px-3 py-2.5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500">Progress</p>
            <h2 className="mt-1 text-lg font-semibold text-white">Track your placement preparation</h2>
            <p className="mt-1 text-sm text-slate-500">A unified view of your placement readiness and module performance.</p>
          </div>
          <button
            type="button"
            onClick={loadData}
            className="rounded-xl border border-slate-800 bg-slate-900 p-2 text-slate-200 transition-colors hover:bg-slate-800"
            aria-label="Refresh progress"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </header>

      {loadingState ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
          <div className="h-3 w-24 rounded bg-slate-800" />
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div className="space-y-2">
              <div className="h-10 w-20 rounded bg-slate-800" />
              <div className="h-3 w-28 rounded bg-slate-800" />
            </div>
            <div className="h-9 w-9 rounded-full bg-slate-800" />
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="animate-pulse rounded-2xl bg-slate-900/60 p-3">
                <div className="h-3 w-16 rounded bg-slate-800" />
                <div className="mt-3 h-2 rounded bg-slate-800" />
                <div className="mt-2 h-3 w-10 rounded bg-slate-800" />
              </div>
            ))}
          </div>
        </motion.div>
      ) : state.error ? (
        <div className="rounded-2xl border border-rose-800/70 bg-rose-950/20 p-4 text-sm text-rose-200">
          <p className="font-medium">{state.error}</p>
          <button onClick={loadData} className="mt-3 rounded-xl border border-rose-700 px-3 py-2 font-medium text-rose-100">Retry</button>
        </div>
      ) : (
        <>
          <section className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
            <div className="grid gap-4 lg:grid-cols-[0.7fr_1.3fr]">
              <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-4">
                <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Overall Progress</p>
                <div className="mt-4 flex items-end gap-4">
                  <div className="text-[2.4rem] font-semibold text-white">{overallProgress}%</div>
                  <div className="space-y-2">
                    <p className="text-sm text-slate-400">{completedModules} of {state.modules.length || 0} Modules Completed</p>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 transition-all duration-700" style={{ width: `${overallProgress}%` }} />
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                {state.modules.map((module) => {
                  const Icon = MODULE_ICON_MAP[module.key] || BarChart3
                  return (
                    <div key={module.key} className="group rounded-3xl bg-slate-900/70 p-3 transition hover:bg-slate-900">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-slate-800 text-slate-300">
                          <Icon size={15} />
                        </div>
                        <span className="text-xs uppercase tracking-[0.24em] text-slate-500">{module.progress}%</span>
                      </div>
                      <p className="mt-3 text-sm font-medium text-white">{module.name}</p>
                      <p className="mt-1 text-xs text-slate-500">{module.detail}</p>
                      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                        <div className="h-full rounded-full bg-violet-500" style={{ width: `${Math.min(100, Math.max(0, Number(module.progress) || 0))}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-950/80 p-3">
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Performance Analytics</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {TAB_CONFIG.map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => handleTabChange(tab.key)}
                    className={`rounded-full border px-3 py-1.5 text-sm transition-colors ${state.selectedTab === tab.key ? 'border-violet-500/40 bg-violet-500/10 text-violet-300' : 'border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800'}`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-2.5">
              <div className="mb-2 flex items-center justify-between gap-4">
                <div>
                  <h4 className="text-sm font-medium text-slate-200">{chartMetricLabel}</h4>
                  <p className="mt-1 text-sm text-slate-500">{selectedModule?.detail || 'Performance data will appear here as you progress.'}</p>
                </div>
                <span className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] uppercase tracking-[0.24em] text-slate-500">Live</span>
              </div>
              {analyticsLoading ? (
                <div className="mt-3 rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-400">
                  Loading analytics…
                </div>
              ) : (
                <>
                  <ProgressChart data={state.analytics} metricLabel={chartMetricLabel} empty={state.analytics.length === 0} />
                  <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                    {chartStats.map((stat) => (
                      <div key={stat.label} className="rounded-xl border border-slate-800 bg-slate-950/70 p-2">
                        <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">{stat.label}</p>
                        <p className="mt-1 text-sm font-semibold text-white">{stat.value}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </section>

          <section className="grid gap-2.5">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-3">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-base font-semibold text-white">Recent Activity</h3>
                <span className="text-xs text-slate-500">Newest first</span>
              </div>
              <div className="mt-2 space-y-2">
                {state.activity.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/50 p-2.5 text-sm text-slate-400">No activity recorded yet.</div>
                ) : (
                  state.activity.map((item, index) => (
                    <div key={`${item.title}-${index}`} className="flex gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-2.5">
                      <div className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-violet-400" />
                      <div className="min-w-0 flex-1">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">{item.timestamp}</p>
                        <p className="mt-1 text-sm font-medium text-slate-100">{item.title}</p>
                        <p className="mt-1 text-sm text-slate-500">{item.description}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={handleOpenHistory}
                disabled={historyLoading}
                className="flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {historyLoading ? <Loader2 size={14} className="animate-spin" /> : <History size={14} />}
                View History
              </button>
              <button type="button" onClick={handleDownload} className="flex items-center justify-center gap-2 rounded-xl bg-violet-500 px-3 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90">
                {state.reportState === 'loading' ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                {state.reportState === 'loading' ? 'Preparing report...' : state.reportState === 'success' ? 'Report downloaded' : state.reportState === 'error' ? 'Download failed' : 'Download Report'}
              </button>
            </div>
            {state.reportState === 'error' && <p className="text-sm text-rose-300">Unable to download the report right now.</p>}
            {state.reportState === 'success' && <p className="text-sm text-emerald-300">Report downloaded successfully.</p>}
          </section>
        </>
      )}

      {historyOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-3 py-4 backdrop-blur-sm">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-2xl rounded-3xl border border-slate-800 bg-slate-950/95 p-4 shadow-2xl">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Module History</p>
                <h3 className="mt-1 text-lg font-semibold text-white">{historyTitle}</h3>
                <p className="mt-1 text-sm text-slate-500">Your real attempts and outcomes from the connected backend.</p>
              </div>
              <button type="button" onClick={() => setHistoryOpen(false)} className="rounded-xl border border-slate-800 bg-slate-900 p-2 text-slate-200 transition-colors hover:bg-slate-800" aria-label="Close history">
                <X size={16} />
              </button>
            </div>

            <div className="mt-4 max-h-[70vh] overflow-auto pr-1">
              {historyLoading ? (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-400">
                  Loading history…
                </div>
              ) : historyError ? (
                <div className="rounded-2xl border border-rose-800 bg-rose-950/20 p-4 text-sm text-rose-200">
                  {historyError}
                </div>
              ) : historyItems.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
                  No history available yet.
                </div>
              ) : (
                <div className="space-y-2">
                  {historyItems.map((item, index) => {
                    const summary = getHistorySummary(item, state.selectedTab)
                    return (
                      <div key={`${state.selectedTab}-${index}`} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Attempt {index + 1}</p>
                            <p className="mt-1 text-sm font-medium text-white">{summary.primary}</p>
                          </div>
                          <span className="text-xs text-slate-500">{formatHistoryDate(item?.submitted_at || item?.date || item?.uploaded_at || item?.created_at)}</span>
                        </div>
                        <div className="mt-2 space-y-1 text-sm text-slate-400">
                          <p><span className="text-slate-500">Result:</span> {summary.secondary}</p>
                          <p><span className="text-slate-500">Details:</span> {summary.detail}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
