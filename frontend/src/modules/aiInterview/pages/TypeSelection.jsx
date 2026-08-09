import React from 'react'
import { useNavigate } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'
import InterviewTypeCard from '../components/InterviewTypeCard'
import { interviewTypes } from '../data/mockData'

export default function TypeSelection() {
  const navigate = useNavigate()
  return (
    <InterviewLayout title="Choose interview type" intro="Pick the experience that matches your goals" showBack>
      <div className="grid gap-4 sm:grid-cols-2">
        {interviewTypes.map((t) => (
          <InterviewTypeCard key={t.id} title={t.title} description={t.description} duration={t.duration} onStart={() => navigate(`/interview/configuration?type=${t.id}`)} />
        ))}
      </div>
    </InterviewLayout>
  )
}
