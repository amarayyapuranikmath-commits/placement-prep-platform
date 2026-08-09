import React from 'react'

export default function QuestionCard({ title, prompt, timer, questionNumber }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">{title}{questionNumber ? ` • Q${questionNumber}` : ''}</p>
          <h3 className="mt-1 text-lg font-semibold text-white">{prompt}</h3>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300">{timer}</div>
      </div>
    </div>
  )
}
