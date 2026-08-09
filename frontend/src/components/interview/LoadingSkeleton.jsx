import React from 'react'

export default function LoadingSkeleton() {
  return (
    <div className="space-y-3 rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
      <div className="h-3 w-24 rounded bg-slate-800" />
      <div className="h-3 w-full rounded bg-slate-800" />
      <div className="h-3 w-4/5 rounded bg-slate-800" />
    </div>
  )
}
