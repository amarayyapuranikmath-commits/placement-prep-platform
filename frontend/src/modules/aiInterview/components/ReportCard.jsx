import React from 'react'

export default function ReportCard({ score = 0, highlights = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Interview Summary</h3>
        <div className="text-2xl font-bold text-white">{score}%</div>
      </div>

      {highlights.length > 0 && (
        <ul className="mt-3 list-disc list-inside text-sm text-slate-300">
          {highlights.map((h, i) => (
            <li key={i}>{h}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
