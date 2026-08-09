import React from 'react'

export default function InterviewTypeCard({ title, description, duration, onStart }) {
  return (
    <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center">●</div>
          <div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400">{description}</p>
          </div>
        </div>
        <div className="px-3 py-1 rounded-2xl bg-slate-900 text-sm text-slate-400">{duration}</div>
      </div>

      <div className="mt-2">
        <button
          type="button"
          onClick={onStart}
          className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
        >
          Start
        </button>
      </div>
    </div>
  )
}
