import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function BackButton({ label = 'Back' }) {
  const navigate = useNavigate()
  return (
    <button
      type="button"
      onClick={() => navigate(-1)}
      className="inline-flex items-center gap-2 text-sm font-medium text-slate-300 transition hover:text-white"
    >
      <span className="text-xl">←</span>
      {label}
    </button>
  )
}
