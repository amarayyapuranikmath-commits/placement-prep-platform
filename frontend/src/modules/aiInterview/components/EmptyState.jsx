import React from 'react'

export default function EmptyState({ title = 'Nothing here', description = '', actionLabel = 'Start', onAction }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-center">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      {description && <p className="mt-2 text-sm text-slate-400">{description}</p>}
      <div className="mt-4">
        <button onClick={onAction} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">{actionLabel}</button>
      </div>
    </div>
  )
}
