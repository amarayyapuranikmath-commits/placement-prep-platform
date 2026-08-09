import React from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'

export default function Live() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'technical'

  const handleEnd = () => navigate(`/interview/report?type=${type}`)

  return (
    <InterviewLayout title="Live interview" intro="Answer the live prompt clearly" showBack>
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="text-lg font-semibold text-white">Prompt</h3>
          <p className="text-sm text-slate-400 mt-2">Describe your approach to the problem and walk through complexity.</p>
        </div>

        <div className="flex justify-end">
          <button onClick={handleEnd} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">Finish</button>
        </div>
      </div>
    </InterviewLayout>
  )
}
