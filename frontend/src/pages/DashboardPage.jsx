import { useEffect, useMemo, useState } from 'react'
import api from '../services/api'
import { getResumeAnalysis, getResumeHistory } from '../services/resumeService'

function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/90 p-4 animate-pulse">
      <div className="h-5 w-1/3 rounded bg-slate-800 mb-3" />
      <div className="h-3 w-2/3 rounded bg-slate-800" />
    </div>
  )
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resumeAnalysis, setResumeAnalysis] = useState(null)

  useEffect(() => {
    let mounted = true

    const loadDashboard = async () => {
      setLoading(true)
      setError(null)
      try {
        const [dashboardResponse, history] = await Promise.all([
          api.get('/dashboard'),
          getResumeHistory(),
        ])

        if (!mounted) return

        const payload = dashboardResponse.data?.data ?? dashboardResponse.data
        setDashboard(payload)

        const latest = history?.find((item) => item?.is_current) || history?.[0] || null
        const latestId = latest?.id ?? latest?._id ?? null

        if (!latestId) {
          setResumeAnalysis(null)
        } else {
          try {
            const analysis = await getResumeAnalysis(latestId)
            if (mounted) {
              setResumeAnalysis(analysis)
            }
          } catch (err) {
            if (mounted) {
              setResumeAnalysis(null)
            }
          }
        }
      } catch (err) {
        if (mounted) {
          setError(err?.response?.data?.message || err.message || 'Unable to load dashboard')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadDashboard()
    return () => {
      mounted = false
    }
  }, [])

  const today = new Date()
  const dateStr = today.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })

  const isLikelyId = (s) => {
    if (!s || typeof s !== 'string') return false
    if (/^[0-9a-fA-F]{24}$/.test(s)) return true
    if (/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(s)) return true
    return false
  }

  const getDisplayName = (user) => {
    if (!user) return null
    const candidates = [
      user.fullName,
      user.full_name,
      user.name,
      user.firstName,
      user.first_name,
      user.username,
      user.email,
    ]
    for (const c of candidates) {
      if (!c) continue
      if (isLikelyId(c)) continue
      if (typeof c === 'string' && c.trim()) return c.trim()
    }
    return null
  }

  const displayName = useMemo(() => getDisplayName(dashboard?.user), [dashboard?.user])

  const isWelcomeBack = displayName ? `Welcome back, ${displayName}` : 'Welcome back 👋'
  const todayFocus = dashboard?.todayFocus ?? []
  const continueLearning = dashboard?.continueLearning ?? []
  const latestInsight = dashboard?.latestInsight ?? {}
  const recentActivity = dashboard?.recentActivity ?? []

  if (loading) {
    return (
      <div className="space-y-6">
        <header className="flex flex-col gap-1">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
          <h1 className="text-2xl font-semibold text-white">{isWelcomeBack}</h1>
          <p className="text-sm text-slate-400">{dateStr}</p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
          <h3 className="text-lg font-semibold text-white">Error</h3>
          <p className="mt-2 text-sm text-slate-400">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-1">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
        <h1 className="text-2xl font-semibold text-white">{isWelcomeBack}</h1>
        <p className="text-sm text-slate-400">{dateStr}</p>
      </header>

      <div className="grid gap-6 xl:grid-cols-12">
        <div className="space-y-6 xl:col-span-4">
          <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="relative">
                <svg width="120" height="120" viewBox="0 0 120 120" className="mx-auto">
                  <g transform="translate(60,60)">
                    <circle r="44" cx="0" cy="0" fill="none" stroke="#0f172a" strokeWidth="10" />
                    <circle
                      r="44"
                      cx="0"
                      cy="0"
                      fill="none"
                      stroke="#60a5fa"
                      strokeWidth="10"
                      strokeLinecap="round"
                      strokeDasharray={`${Math.max(0, Math.min(100, resumeAnalysis?.ats_score ?? 0)) / 100 * (2 * Math.PI * 44)} ${2 * Math.PI * 44}`}
                      transform="rotate(-90)"
                    />
                  </g>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="text-4xl font-bold text-blue-400">
                    {resumeAnalysis?.ats_score !== null && resumeAnalysis?.ats_score !== undefined
                      ? Math.round(resumeAnalysis.ats_score)
                      : '--'}
                  </div>
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm font-semibold text-white">ATS Score</div>
                <div className="text-xs text-slate-400">
                  {resumeAnalysis?.ats_score !== null && resumeAnalysis?.ats_score !== undefined
                    ? resumeAnalysis.quality_label || 'Reviewed'
                    : 'Not analyzed yet'}
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <h2 className="text-sm font-semibold text-white">Today's Focus</h2>
                {todayFocus.length > 0 ? (
                  <p className="mt-3 text-sm leading-6 text-slate-300">{todayFocus[0].description}</p>
                ) : (
                  <p className="mt-3 text-sm leading-6 text-slate-400">No focus available. Try completing a module for a recommendation.</p>
                )}
              </div>
              {todayFocus.length > 0 && (
                <a
                  href={todayFocus[0].route}
                  className="inline-flex h-11 items-center rounded-2xl bg-accent px-4 text-sm font-semibold text-slate-950"
                >
                  Continue
                </a>
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <h2 className="text-sm font-semibold text-white">Latest AI Insight</h2>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  {latestInsight?.text ? latestInsight.text : 'No insights available yet.'}
                </p>
              </div>
              <a
                href="/ai-insights"
                className="inline-flex h-10 items-center rounded-2xl border border-slate-700 bg-slate-900/80 px-4 text-sm font-semibold text-white"
              >
                Open
              </a>
            </div>
          </section>
        </div>

        <div className="space-y-6 xl:col-span-8">
          <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
            <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-sm font-semibold text-white">Continue Learning</h2>
                <p className="mt-1 text-sm text-slate-400">Pick up where you left off.</p>
              </div>
            </div>
            <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {continueLearning.map((c, i) => (
                <div key={i} className="flex h-32 flex-col justify-between rounded-3xl border border-slate-800 bg-slate-900/80 p-4">
                  <div>
                    <div className="text-sm font-semibold text-white">{c.name}</div>
                    <div className="mt-2 text-sm leading-6 text-slate-400">{c.status}</div>
                  </div>
                  <a
                    href={c.route}
                    className="inline-flex h-10 items-center justify-center rounded-2xl bg-accent px-4 text-sm font-semibold text-slate-950"
                  >
                    Continue
                  </a>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6">
            <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-sm font-semibold text-white">Recent Activity</h2>
                <p className="mt-1 text-sm text-slate-400">Your latest actions in one place.</p>
              </div>
              <span className="text-xs uppercase tracking-[0.24em] text-slate-500">Latest 5</span>
            </div>
            <div className="mt-4 space-y-3">
              {recentActivity.slice(0, 5).map((a, i) => (
                <div key={i} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-white">{a.title}</div>
                      <div className="mt-1 text-sm text-slate-400">{a.timestamp ? new Date(a.timestamp).toLocaleString() : 'No timestamp'}</div>
                    </div>
                    <span className="rounded-full bg-slate-800/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                      {a.type}
                    </span>
                  </div>
                </div>
              ))}
              {recentActivity.length === 0 && (
                <p className="text-sm text-slate-500">No recent activity. Start by completing your profile or trying a module.</p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
