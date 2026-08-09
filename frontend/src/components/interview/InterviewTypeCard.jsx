import React from 'react'

export default function InterviewTypeCard({ icon: Icon, title, description, duration, onStart }) {
  return (
    <div className="flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-950/90 p-4 transition hover:border-slate-700 hover:bg-slate-900">
      <div className="space-y-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/10 text-accent">
          {Icon ? <Icon size={18} /> : <span className="text-accent">●</span>}
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <div className="text-sm text-slate-500">{duration}</div>
        <button type="button" onClick={onStart} className="rounded-2xl bg-accent px-3 py-2 text-sm font-semibold text-slate-950">Start</button>
      </div>
    </div>
  )
}