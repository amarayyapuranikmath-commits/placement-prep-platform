import { ArrowRight, Brain, Code2, FileText, MessageSquare, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

const BrandMark = () => (
  <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-violet-500/25 bg-violet-500/10 p-1">
    <svg viewBox="0 0 64 64" className="h-7 w-7 text-violet-300" fill="none" aria-hidden="true">
      <path d="M20 16h24a4 4 0 0 1 4 4v14a8 8 0 0 1-8 8h-4v8h-8v-8h-4a8 8 0 0 1-8-8V20a4 4 0 0 1 4-4Z" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
      <path d="M24 24h16" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M24 32h10" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M30 40v-6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  </div>
)

const features = [
  {
    title: 'Resume Analyzer',
    description: 'Analyze your resume and identify ATS improvements that strengthen your application.',
    icon: FileText,
  },
  {
    title: 'Coding Practice',
    description: 'Build problem-solving skills with focused coding practice tailored to placement rounds.',
    icon: Code2,
  },
  {
    title: 'AI Interview',
    description: 'Practice realistic interviews and refine your responses with structured feedback.',
    icon: MessageSquare,
  },
  {
    title: 'Aptitude',
    description: 'Improve speed and accuracy with targeted aptitude exercises and steady progress tracking.',
    icon: Brain,
  },
]

const steps = [
  {
    title: 'Create your profile',
    description: 'Set up your account and start with a preparation plan that fits your goals.',
  },
  {
    title: 'Practice across modules',
    description: 'Work through interviews, coding, aptitude, and resume tasks in one calm workflow.',
  },
  {
    title: 'Track your progress',
    description: 'Keep an eye on results and improvements as you prepare with confidence.',
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.16),_transparent_30%),linear-gradient(135deg,_#020617_0%,_#0f172a_100%)] text-slate-100">
      <header className="sticky top-0 z-20 border-b border-slate-800/70 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <BrandMark />
            <div className="leading-tight">
              <p className="text-sm font-semibold text-white">Placement Prep</p>
              <p className="text-xs text-slate-500">Placement preparation platform</p>
            </div>
          </Link>

          <nav className="flex items-center gap-2 sm:gap-3">
            <Link to="/login" className="rounded-full px-3 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-900 hover:text-white">
              Login
            </Link>
            <Link to="/register" className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition-colors hover:bg-indigo-400">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
        <section className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1 text-sm text-violet-200">
              <Sparkles size={15} />
              A smarter way to prepare
            </div>
            <h1 className="mt-6 text-4xl font-semibold leading-tight text-white sm:text-5xl">
              Prepare Smarter. Get Placement Ready.
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-400">
              One platform to prepare for technical interviews, coding assessments, aptitude tests, and resume screening — all in one place.
            </p>
          </div>

          <div className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-4 shadow-xl shadow-slate-950/40 sm:p-6">
            <div className="rounded-[24px] border border-slate-800 bg-slate-900/80 p-4 sm:p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Preparation overview</p>
                  <p className="mt-1 text-sm font-medium text-white">A focused view of your readiness</p>
                </div>
                <span className="rounded-full border border-violet-500/20 bg-violet-500/10 px-2.5 py-1 text-xs font-medium text-violet-300">
                  Live
                </span>
              </div>

              <div className="mt-5 space-y-3">
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Resume</p>
                      <p className="mt-1 text-sm font-medium text-white">ATS-ready profile</p>
                    </div>
                    <span className="text-sm font-semibold text-white">82%</span>
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Interview</p>
                      <p className="mt-1 text-sm font-medium text-white">Practice sessions</p>
                    </div>
                    <span className="text-sm font-semibold text-white">6</span>
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Aptitude</p>
                      <p className="mt-1 text-sm font-medium text-white">Drills completed</p>
                    </div>
                    <span className="text-sm font-semibold text-white">14</span>
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Coding</p>
                      <p className="mt-1 text-sm font-medium text-white">Problem streak</p>
                    </div>
                    <span className="text-sm font-semibold text-white">+3</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-20">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Platform features</p>
            <h2 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">Everything you need to prepare with clarity.</h2>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div key={feature.title} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 transition-colors hover:border-slate-700 hover:bg-slate-900/70">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-violet-500/20 bg-violet-500/10 text-violet-300">
                    <Icon size={18} />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-white">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-7 text-slate-400">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        <section className="mt-20 rounded-[28px] border border-slate-800 bg-slate-950/70 p-6 sm:p-8 lg:p-10">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">How it works</p>
            <h2 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">A focused path from first step to confident prep.</h2>
          </div>

          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step.title} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-violet-500/10 text-sm font-semibold text-violet-300">
                  {index + 1}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-white">{step.title}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-400">{step.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-20 rounded-[28px] border border-slate-800 bg-gradient-to-br from-slate-950 to-slate-900/80 p-8 sm:p-10">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Everything in one place</p>
            <h2 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">Everything you need to prepare with confidence.</h2>
            <p className="mt-4 text-base leading-8 text-slate-400">
              Placement Prep brings preparation, performance tracking, and personalized insights into one clear experience so you can focus on improvement rather than scattered tools.
            </p>
            <div className="mt-8">
              <Link to="/register" className="inline-flex items-center justify-center gap-2 rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition-colors hover:bg-indigo-400">
                Start your placement preparation today
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800/80 bg-slate-950/60">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <div>
            <p className="font-semibold text-slate-300">Placement Prep</p>
            <p className="mt-1">A focused platform for interview, coding, aptitude, and resume preparation.</p>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="transition-colors hover:text-white">Login</Link>
            <Link to="/register" className="transition-colors hover:text-white">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
