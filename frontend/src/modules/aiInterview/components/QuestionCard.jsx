import React from 'react'

export default function QuestionCard({ title = 'Problem', prompt = 'Explain your approach.', timer = '00:02:00' }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="mt-2 text-sm text-slate-400">{prompt}</p>
        </div>
        <div className="ml-4 text-sm text-slate-300">{timer}</div>
      </div>
    </div>
  )
}
