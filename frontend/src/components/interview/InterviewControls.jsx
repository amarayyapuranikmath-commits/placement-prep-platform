import React from 'react'
import { MicOff, MonitorOff, Repeat2, PauseCircle, PlayCircle, Square, Send } from 'lucide-react'

export default function InterviewControls({ isMuted = false, isCameraOn = true, onMute, onCamera, onEnd, onSubmit, isSubmitting = false, canSubmit = true, onPause, onResume, onRepeat, isPaused = false }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-3">
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={onMute} className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
          {isMuted ? <MicOff size={16} /> : <MicOff size={16} />}
          {isMuted ? 'Unmute' : 'Mute'}
        </button>
        <button type="button" onClick={onCamera} className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
          {isCameraOn ? <MonitorOff size={16} /> : <MonitorOff size={16} />}
          {isCameraOn ? 'Camera off' : 'Camera on'}
        </button>
        <button type="button" onClick={onRepeat} className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
          <Repeat2 size={16} />
          Repeat
        </button>
        <button type="button" onClick={onPause} disabled={isPaused} className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
          <PauseCircle size={16} />
          Pause
        </button>
        <button type="button" onClick={onResume} disabled={!isPaused} className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
          <PlayCircle size={16} />
          Resume
        </button>
        <button type="button" onClick={onSubmit} disabled={!canSubmit || isSubmitting} className="flex items-center gap-2 rounded-2xl border border-accent/40 bg-accent/10 px-3 py-2 text-sm font-semibold text-accent disabled:cursor-not-allowed disabled:opacity-60">
          <Send size={16} />
          {isSubmitting ? 'Submitting...' : 'Submit answer'}
        </button>
        <button type="button" onClick={onEnd} className="flex items-center gap-2 rounded-2xl bg-accent px-3 py-2 text-sm font-semibold text-slate-950">
          <Square size={16} />
          End
        </button>
      </div>
    </div>
  )
}
