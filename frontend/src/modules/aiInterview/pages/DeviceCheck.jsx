import React from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'
import DeviceCheckPanel from '../components/DeviceCheckPanel'
import { deviceChecklist } from '../data/mockData'

export default function DeviceCheck() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'technical'

  const handleStart = () => navigate(`/interview/live?type=${type}`)

  return (
    <InterviewLayout title="Device check" intro="Confirm your setup before starting" showBack>
      <DeviceCheckPanel checks={deviceChecklist} />
      <div className="flex justify-end">
        <button onClick={handleStart} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">Begin interview</button>
      </div>
    </InterviewLayout>
  )
}
