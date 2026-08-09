import React from 'react'
import { useNavigate } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'

const rows = [
  { id: 1, type: 'Technical', date: '2026-07-01', score: 82 },
  { id: 2, type: 'Behavioral', date: '2026-06-12', score: 90 },
]

export default function History() {
  const navigate = useNavigate()
  return (
    <InterviewLayout title="History" intro="Recent interview sessions" showBack>
      <div className="space-y-3">
        {rows.map((r) => (
          <div key={r.id} className="rounded-xl border border-slate-800 bg-slate-950 p-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white">{r.type}</div>
              <div className="text-sm text-slate-400">{r.date}</div>
            </div>
            <div className="text-sm font-semibold text-white">{r.score}%</div>
          </div>
        ))}

        <div className="flex justify-end">
          <button onClick={() => navigate('/interview')} className="rounded-2xl border border-slate-800 px-4 py-2 text-sm font-semibold text-slate-100">Back</button>
        </div>
      </div>
    </InterviewLayout>
  )
}
