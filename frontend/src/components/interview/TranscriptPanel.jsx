import React from 'react'

export default function TranscriptPanel({ transcript = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">Transcript</h3>
        <span className="text-xs text-slate-500">Live</span>
      </div>
      <div className="mt-3 space-y-3">
        {transcript.length === 0 ? (
          <p className="text-sm text-slate-500">No transcript yet.</p>
        ) : (
          transcript.map((item, index) => (
            <div key={`${item.speaker}-${item.timestamp || index}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{item.speaker}</p>
                {item.timestamp && (
                  <p className="text-xs text-slate-500">{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                )}
              </div>
              <p className="mt-1 text-sm text-slate-300">{item.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
