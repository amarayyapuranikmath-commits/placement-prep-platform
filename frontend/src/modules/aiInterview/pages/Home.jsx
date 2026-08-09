import React from 'react'
import { useNavigate } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'

export default function Home() {
  const navigate = useNavigate()
  return (
    <InterviewLayout title="AI Interview" intro="Practice realistic interviews with concise, actionable feedback." >
      <div className="space-y-4">
        <p className="text-sm text-slate-400">Start a new mock interview or review your previous sessions.</p>
        <div className="flex gap-3">
          <button onClick={() => navigate('/interview/type')} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">New interview</button>
          <button onClick={() => navigate('/interview/history')} className="rounded-2xl border border-slate-800 px-4 py-2 text-sm font-semibold text-slate-100">History</button>
        </div>
      </div>
    </InterviewLayout>
  )
}
