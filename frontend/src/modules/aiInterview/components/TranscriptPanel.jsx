import React from 'react'

export default function TranscriptPanel({ transcript = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
      <h4 className="text-sm font-semibold text-white">Transcript</h4>
      <div className="mt-3 max-h-48 overflow-auto text-sm text-slate-300 space-y-3">
        {transcript.length === 0 ? (
          <div className="text-slate-500">No transcript yet.</div>
        ) : (
          transcript.map((t, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="text-xs font-semibold text-accent">{t.who}</div>
              <div className="text-sm text-slate-300">{t.text}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
