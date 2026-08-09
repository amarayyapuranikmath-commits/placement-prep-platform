import React from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'

export default function Report() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'technical'

  return (
    <InterviewLayout title="Report" intro="Summary and feedback" showBack>
      <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
        <h3 className="text-lg font-semibold text-white">Score</h3>
        <p className="text-2xl font-bold text-white mt-2">85%</p>
        <h4 className="mt-4 text-sm font-semibold text-white">Highlights</h4>
        <ul className="mt-2 text-sm text-slate-400 list-disc list-inside">
          <li>Clear structure</li>
          <li>Good complexity explanation</li>
        </ul>
      </div>

      <div className="flex gap-3 justify-end">
        <button onClick={() => navigate('/interview')} className="rounded-2xl border border-slate-800 px-4 py-2 text-sm font-semibold text-slate-100">Return</button>
        <button onClick={() => navigate('/interview')} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">Done</button>
      </div>
    </InterviewLayout>
  )
}
