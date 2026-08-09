import React, { useEffect, useState } from 'react'
import { CheckCircle2, Mic, Monitor, Radio, Sparkles, RefreshCw } from 'lucide-react'

export default function DeviceCheck({ onBegin, isStarting = false }) {
  const [hasCamera, setHasCamera] = useState(null)
  const [hasMicrophone, setHasMicrophone] = useState(null)
  const [hasSpeaker, setHasSpeaker] = useState(null)
  const [cameraPermission, setCameraPermission] = useState('unknown')
  const [micPermission, setMicPermission] = useState('unknown')
  const [online, setOnline] = useState(navigator.onLine)
  const [supported, setSupported] = useState(Boolean(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices))
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const onOnline = () => setOnline(true)
    const onOffline = () => setOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)

    detectDevices()

    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const detectDevices = async () => {
    setChecking(true)
    setSupported(Boolean(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices))
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      setHasCamera(devices.some((d) => d.kind === 'videoinput'))
      setHasMicrophone(devices.some((d) => d.kind === 'audioinput'))
      setHasSpeaker(devices.some((d) => d.kind === 'audiooutput'))

      // Query permissions where available
      try {
        if (navigator.permissions && navigator.permissions.query) {
          const camPerm = await navigator.permissions.query({ name: 'camera' })
          const micPerm = await navigator.permissions.query({ name: 'microphone' })
          setCameraPermission(camPerm.state)
          setMicPermission(micPerm.state)
        }
      } catch (e) {
        // ignore
      }
    } catch (err) {
      setHasCamera(false)
      setHasMicrophone(false)
      setHasSpeaker(false)
    }
    setChecking(false)
  }

  const requestPermissions = async () => {
    setChecking(true)
    try {
      // request for both audio and video to surface permission prompts
      await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
      // close tracks immediately - this is only to obtain permission
      try {
        const s = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        s.getTracks().forEach((t) => t.stop())
      } catch (e) {
        // ignore
      }
      await detectDevices()
    } catch (err) {
      await detectDevices()
    }
    setChecking(false)
  }

  const canStart = !checking && online && supported && hasCamera && hasMicrophone

  const statusIcon = (ok) => (ok ? <CheckCircle2 size={18} className="text-accent" /> : <RefreshCw size={18} className="text-rose-500" />)

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10 text-accent">
          <Sparkles size={18} />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-white">Device check</h3>
          <p className="mt-1 text-sm text-slate-400">A quick pass so your practice session starts smoothly.</p>
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-3">
          <div>
            <p className="text-sm font-medium text-slate-100">Microphone</p>
            <p className="text-sm text-slate-400">{checking ? 'Checking…' : micPermission === 'denied' ? 'Permission denied' : hasMicrophone ? 'Detected' : 'No microphone found'}</p>
          </div>
          {statusIcon(!checking && hasMicrophone && micPermission !== 'denied')}
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-3">
          <div>
            <p className="text-sm font-medium text-slate-100">Camera</p>
            <p className="text-sm text-slate-400">{checking ? 'Checking…' : cameraPermission === 'denied' ? 'Permission denied' : hasCamera ? 'Detected' : 'No camera found'}</p>
          </div>
          {statusIcon(!checking && hasCamera && cameraPermission !== 'denied')}
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-3">
          <div>
            <p className="text-sm font-medium text-slate-100">Speaker</p>
            <p className="text-sm text-slate-400">{checking ? 'Checking…' : hasSpeaker ? 'Detected' : 'No speaker output detected'}</p>
          </div>
          {statusIcon(!checking && hasSpeaker)}
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-3">
          <div>
            <p className="text-sm font-medium text-slate-100">Internet</p>
            <p className="text-sm text-slate-400">{online ? 'Online' : 'Offline'}</p>
          </div>
          {statusIcon(online)}
        </div>
      </div>

      <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-300">
        <p className="font-medium text-slate-100">Interview tip</p>
        <p className="mt-1 text-slate-400">Keep answers concise, structured, and slightly slower than your usual pace.</p>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <div>
          <button type="button" onClick={requestPermissions} className="rounded-2xl border border-slate-800 px-4 py-2 text-sm text-slate-100 mr-3">Retry detection</button>
        </div>
        <div>
          <button type="button" onClick={onBegin} disabled={!canStart || isStarting} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60">{isStarting ? 'Starting...' : 'Start interview'}</button>
        </div>
      </div>
    </div>
  )
}