import React from 'react'

export default function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      <div className="h-6 w-48 rounded bg-slate-800/40" />
      <div className="h-40 rounded bg-slate-800/30" />
    </div>
  )
}
