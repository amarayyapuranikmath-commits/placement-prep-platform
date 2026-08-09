import React from 'react'

export default function HistoryTable({ rows = [], onOpen }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-900/80 text-left text-slate-400">
          <tr>
            <th className="px-3 py-3 font-medium">Date</th>
            <th className="px-3 py-3 font-medium">Interview Type</th>
            <th className="px-3 py-3 font-medium">Role</th>
            <th className="px-3 py-3 font-medium">Duration</th>
            <th className="px-3 py-3 font-medium">Score</th>
            <th className="px-3 py-3 font-medium">Status</th>
            <th className="px-3 py-3 font-medium">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-950/80 text-slate-300">
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="px-3 py-3">{row.date}</td>
              <td className="px-3 py-3">{row.type}</td>
              <td className="px-3 py-3">{row.role}</td>
              <td className="px-3 py-3">{row.duration}</td>
              <td className="px-3 py-3">{row.score}</td>
              <td className="px-3 py-3">{row.status}</td>
              <td className="px-3 py-3">
                <button type="button" onClick={onOpen} className="rounded-2xl border border-slate-800 px-3 py-2 text-sm text-slate-100">View report</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
