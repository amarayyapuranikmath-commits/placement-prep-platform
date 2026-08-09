import React from 'react'

export default function DeviceCheckPanel({ checks }) {
  return (
    <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-4">
      <h3 className="text-lg font-semibold text-white">Device check</h3>
      <div className="grid gap-3 sm:grid-cols-2">
        {checks.map((c) => (
          <div key={c.label} className="rounded-xl border border-slate-800 bg-slate-950 p-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white">{c.label}</div>
              <div className="text-sm text-slate-400">{c.status}</div>
            </div>
            <div className="text-emerald-300">●</div>
          </div>
        ))}
      </div>
    </div>
  )
}
