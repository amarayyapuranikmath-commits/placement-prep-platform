import React from 'react'

export default function InterviewLayout({ title, intro, children, showBack = false, onBack }) {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
        {showBack && (
          <div className="mb-4">
            <button type="button" onClick={onBack} className="inline-flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800">
              ← Back
            </button>
          </div>
        )}
        <p className="text-sm uppercase tracking-[0.24em] text-slate-500">{title}</p>
        <h1 className="mt-2 text-3xl font-semibold text-white">{intro}</h1>
      </div>

      <div>{children}</div>
    </div>
  )
}