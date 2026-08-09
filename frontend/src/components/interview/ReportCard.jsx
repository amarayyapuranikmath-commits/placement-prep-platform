import React from 'react'

export default function ReportCard({ score, summary, strengths = [], improvements = [], communication, technical, topics = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-400">Interview report</p>
          <h3 className="text-xl font-semibold text-white">Overall score</h3>
        </div>
        <div className="rounded-2xl bg-accent/10 px-4 py-3 text-3xl font-semibold text-accent">{score}/100</div>
      </div>

      <p className="mt-4 text-sm text-slate-300">{summary}</p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <h4 className="text-sm font-semibold text-white">Strengths</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-400">
            {strengths.map((item) => <li key={item}>• {item}</li>)}
          </ul>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <h4 className="text-sm font-semibold text-white">Areas to improve</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-400">
            {improvements.map((item) => <li key={item}>• {item}</li>)}
          </ul>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <h4 className="text-sm font-semibold text-white">Communication feedback</h4>
          <p className="mt-2 text-sm text-slate-400">{communication}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <h4 className="text-sm font-semibold text-white">Technical feedback</h4>
          <p className="mt-2 text-sm text-slate-400">{technical}</p>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <h4 className="text-sm font-semibold text-white">Recommended topics</h4>
        <div className="mt-3 flex flex-wrap gap-2">
          {topics.map((topic) => (
            <span key={topic} className="rounded-full border border-slate-800 px-3 py-1 text-sm text-slate-400">{topic}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
