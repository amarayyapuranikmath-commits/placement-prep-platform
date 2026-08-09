import React from 'react'

export default function InterviewControls({ onMute, onCamera, onEnd, isMuted = false, isCameraOn = true }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-3 flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <button onClick={onMute} className="rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">{isMuted ? 'Unmute' : 'Mute'}</button>
        <button onClick={onCamera} className="rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">{isCameraOn ? 'Camera off' : 'Camera on'}</button>
      </div>

      <div className="flex items-center gap-2">
        <button onClick={onEnd} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">End interview</button>
      </div>
    </div>
  )
}
