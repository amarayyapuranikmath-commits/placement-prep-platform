import React from 'react'
import BackButton from './BackButton'

export default function InterviewLayout({ title, intro, children, showBack = false }) {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        {showBack && (
          <div className="mb-4">
            <BackButton label="Back to interviews" />
          </div>
        )}

        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">{title}</p>
          <h1 className="text-3xl font-semibold text-white">{intro}</h1>
        </div>
      </div>

      <div className="grid gap-6">{children}</div>
    </div>
  )
}
