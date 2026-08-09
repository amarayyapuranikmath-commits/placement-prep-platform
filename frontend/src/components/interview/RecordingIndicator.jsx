import React from 'react'

export default function RecordingIndicator({ isRecording = false, isPaused = false, isMuted = false, isConnected = true, statusText = '' }) {
  let displayText = statusText
  if (!displayText) {
    if (!isConnected) displayText = 'Disconnected'
    else if (isPaused) displayText = 'Paused'
    else if (isMuted) displayText = 'Muted'
    else displayText = isRecording ? 'Recording' : 'Standby'
  }

  const bgClass = !isConnected ? 'bg-rose-500/10 text-rose-400' : isPaused ? 'bg-amber-500/10 text-amber-300' : isMuted ? 'bg-slate-700/10 text-slate-400' : isRecording ? 'bg-red-500/10 text-red-400' : 'bg-slate-900 text-slate-300'
  const dotClass = !isConnected ? 'bg-rose-400' : isPaused ? 'bg-amber-400' : isMuted ? 'bg-slate-600' : isRecording ? 'bg-red-500' : 'bg-slate-600'

  return (
    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm ${bgClass}`}>
      <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />
      {displayText}
    </div>
  )
}
