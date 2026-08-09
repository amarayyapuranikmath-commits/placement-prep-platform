import React from 'react'

export default function HistoryTable({ rows = [], onOpen }) {
  return (
    <div className="space-y-3">
      {rows.map((r) => (
        <div key={r.id} className="rounded-xl border border-slate-800 bg-slate-950 p-3 flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-white">{r.type}</div>
            <div className="text-sm text-slate-400">{r.date}</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-sm font-semibold text-white">{r.score}%</div>
            <button onClick={() => onOpen?.(r)} className="rounded-xl border border-slate-800 px-3 py-2 text-sm text-slate-100">Open</button>
          </div>
        </div>
      ))}
    </div>
  )
}
