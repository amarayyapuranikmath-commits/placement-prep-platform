import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import InterviewLayout from '../components/InterviewLayout'
import ConfigurationForm from '../components/ConfigurationForm'
import { defaultConfig, interviewFormOptions } from '../data/mockData'

export default function Configuration() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'technical'

  const [values, setValues] = useState(defaultConfig)

  const handleChange = (e) => setValues((p) => ({ ...p, [e.target.name]: e.target.value }))
  const handleSubmit = (e) => {
    e.preventDefault()
    navigate(`/interview/device-check?type=${type}`)
  }

  return (
    <InterviewLayout title="Configuration" intro="Adjust role and duration" showBack>
      <ConfigurationForm values={values} options={interviewFormOptions} onChange={handleChange} onSubmit={handleSubmit} submitting={false} />
    </InterviewLayout>
  )
}
