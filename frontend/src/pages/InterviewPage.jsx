import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Code2, MessageSquare, Mic, Monitor, Radio, Server, Sparkles, TimerReset, User, Users, Zap } from 'lucide-react'
import { createInterviewSession, submitInterviewTurn, getInterviewQuestion } from '../services/interview/interviewService'
import InterviewLayout from '../components/interview/InterviewLayout'
import InterviewTypeCard from '../components/interview/InterviewTypeCard'
import ConfigurationForm from '../components/interview/ConfigurationForm'
import DeviceCheck from '../components/interview/DeviceCheck'
import QuestionCard from '../components/interview/QuestionCard'
import TranscriptPanel from '../components/interview/TranscriptPanel'
import RecordingIndicator from '../components/interview/RecordingIndicator'
import InterviewControls from '../components/interview/InterviewControls'
import ReportCard from '../components/interview/ReportCard'
import HistoryTable from '../components/interview/HistoryTable'
import EmptyState from '../components/interview/EmptyState'
import LoadingSkeleton from '../components/interview/LoadingSkeleton'

const TYPES = [
  { id: 'technical', title: 'Technical Interview', description: 'Algorithms, data structures, and problem solving.', duration: '40m', icon: Code2 },
  { id: 'hr', title: 'HR Interview', description: 'Culture fit, communication, and role alignment.', duration: '15m', icon: User },
  { id: 'behavioral', title: 'Behavioral Interview', description: 'STAR stories and leadership-oriented questions.', duration: '20m', icon: Users },
  { id: 'system', title: 'System Design', description: 'Architecture thinking and trade-off discussions.', duration: '45m', icon: Server },
  { id: 'mixed', title: 'Mixed Interview', description: 'Balanced prep across multiple interview styles.', duration: '30m', icon: Zap },
]

const INITIAL_CONFIG = {
  role: 'Software Engineer',
  companyType: 'Product',
  experience: 'Mid',
  duration: '30m',
  language: 'English',
  voice: 'Neutral',
}

const INITIAL_TRANSCRIPT = [
  { speaker: 'AI', text: 'Let’s begin with a short introduction and your current focus area.' },
  { speaker: 'You', text: 'I am preparing for a product-engineering role and I want to sharpen my system design communication.' },
]

const HISTORY_ROWS = [
  { id: 1, date: 'Jul 24, 2026', type: 'Technical Interview', role: 'Software Engineer', duration: '40m', score: '84', status: 'Completed' },
  { id: 2, date: 'Jul 18, 2026', type: 'Behavioral Interview', role: 'Product Engineer', duration: '20m', score: '88', status: 'Completed' },
]

export default function InterviewPage() {
  const navigate = useNavigate()
  const [view, setView] = useState('home')
  const [selectedType, setSelectedType] = useState(TYPES[0])
  const [config, setConfig] = useState(INITIAL_CONFIG)
  const [transcript, setTranscript] = useState(INITIAL_TRANSCRIPT)
  const [isMuted, setIsMuted] = useState(false)
  const [isCameraOn, setIsCameraOn] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [sessionError, setSessionError] = useState('')
  const [configError, setConfigError] = useState('')
  const [sessionData, setSessionData] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [answerText, setAnswerText] = useState('')
  const [speechSupported, setSpeechSupported] = useState(false)
  const [isSpeechRecording, setIsSpeechRecording] = useState(false)
  const [speechStatus, setSpeechStatus] = useState('')
  const [speechError, setSpeechError] = useState('')
  const recognitionRef = useRef(null)
  const answerRef = useRef(null)
  const answerBaseRef = useRef('')
  const interimTranscriptRef = useRef('')
  const finalizedTranscriptRef = useRef('')
  const isSpeechRecordingRef = useRef(false)
  const stopRequestedRef = useRef(false)
  const autoRestartTimerRef = useRef(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submissionError, setSubmissionError] = useState('')
  const [reportData, setReportData] = useState(null)
  const [reportError, setReportError] = useState('')
  const [isReportLoading, setIsReportLoading] = useState(false)
  const [mediaSupported, setMediaSupported] = useState(false)
  const [mediaInitializing, setMediaInitializing] = useState(false)
  const [mediaError, setMediaError] = useState('')
  const [mediaStatus, setMediaStatus] = useState('')
  const [mediaStream, setMediaStream] = useState(null)
  const videoRef = useRef(null)
  const [isRecordingState, setIsRecordingState] = useState(false)
  const [questionNumber, setQuestionNumber] = useState(1)
  const [isPaused, setIsPaused] = useState(false)
  const [timerRemaining, setTimerRemaining] = useState(0)
  const [timerExpiresAt, setTimerExpiresAt] = useState(null)
  const timerRef = useRef(null)
  const pendingLaunchRef = useRef(0)

  const cancelPendingLaunch = () => {
    pendingLaunchRef.current += 1
    setIsLoading(false)
    setSessionError('')
  }

  const commitSpeechText = (segment) => {
    const cleaned = `${segment || ''}`.replace(/\s+/g, ' ').trim()
    if (!cleaned) return

    const existing = finalizedTranscriptRef.current.trim()
    if (!existing) {
      finalizedTranscriptRef.current = cleaned
      return
    }

    const normalizedExisting = existing.toLowerCase()
    const normalizedSegment = cleaned.toLowerCase()
    if (normalizedExisting.endsWith(normalizedSegment) || normalizedExisting.includes(normalizedSegment)) {
      return
    }

    finalizedTranscriptRef.current = `${existing} ${cleaned}`.trim()
  }

  const syncSpeechAnswerText = () => {
    const merged = [finalizedTranscriptRef.current, interimTranscriptRef.current].filter(Boolean).join(' ').trim()
    setAnswerText(merged)
  }

  const startSpeechRecognition = async () => {
    if (!speechSupported || isSpeechRecordingRef.current) return

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setSpeechSupported(false)
      setSpeechStatus('Voice input is not supported in this browser.')
      return
    }

    stopRequestedRef.current = false
    setSpeechError('')
    setSpeechStatus('Requesting microphone permission...')

    try {
      if (navigator.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        stream.getTracks().forEach((track) => track.stop())
      }
    } catch (permissionError) {
      setSpeechError('Microphone permission denied. Please allow microphone access and try again.')
      setSpeechStatus('Microphone unavailable')
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = 'en-IN'
      recognition.interimResults = true
      recognition.maxAlternatives = 1
      recognition.continuous = true

      recognition.onstart = () => {
        console.debug('[speech] recognition started')
        isSpeechRecordingRef.current = true
        setIsSpeechRecording(true)
        setSpeechStatus('Listening...')
        finalizedTranscriptRef.current = answerRef.current || ''
        interimTranscriptRef.current = ''
        syncSpeechAnswerText()
      }

      recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i]
          const transcript = `${result[0].transcript || ''}`.replace(/\s+/g, ' ').trim()
          if (result.isFinal) {
            finalTranscript = finalTranscript ? `${finalTranscript} ${transcript}` : transcript
          } else {
            interimTranscript = interimTranscript ? `${interimTranscript} ${transcript}` : transcript
          }
        }

        console.debug('[speech] interim transcript', interimTranscript)
        console.debug('[speech] final transcript', finalTranscript)

        if (finalTranscript) {
          commitSpeechText(finalTranscript)
          interimTranscriptRef.current = ''
          syncSpeechAnswerText()
          setSpeechStatus('Recognized text updating...')
        } else if (interimTranscript) {
          interimTranscriptRef.current = interimTranscript
          syncSpeechAnswerText()
          setSpeechStatus('Listening...')
        }
      }

      recognition.onerror = (event) => {
        let message = 'Speech recognition failed.'
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') message = 'Microphone permission denied.'
        if (event.error === 'no-speech') message = 'No speech detected. Please try again.'
        if (event.error === 'audio-capture') message = 'Microphone unavailable. Check your device.'
        if (event.error === 'network') message = 'Network interruption occurred. Please try again.'
        console.debug('[speech] error', event.error, message)
        setSpeechError(message)
        setSpeechStatus('Speech recognition failed')
        isSpeechRecordingRef.current = false
        setIsSpeechRecording(false)
        recognitionRef.current = null
        try {
          recognition.stop()
        } catch (stopError) {
          console.debug('[speech] stop error', stopError)
        }
      }

      recognition.onend = () => {
        console.debug('[speech] recognition ended')
        isSpeechRecordingRef.current = false
        setIsSpeechRecording(false)
        recognitionRef.current = null
        if (stopRequestedRef.current) {
          setSpeechStatus('Recording stopped')
          return
        }
        setSpeechStatus('Recognition complete')
        if (autoRestartTimerRef.current) {
          window.clearTimeout(autoRestartTimerRef.current)
        }
        autoRestartTimerRef.current = window.setTimeout(() => {
          if (!stopRequestedRef.current) {
            console.debug('[speech] auto-restarting recognition')
            void startSpeechRecognition()
          }
        }, 400)
      }

      recognition.onspeechend = () => {
        setSpeechStatus('Processing speech...')
      }

      recognition.start()
      recognitionRef.current = recognition
    } catch (error) {
      console.debug('[speech] setup error', error)
      setSpeechError('Unable to start voice recording.')
      setSpeechStatus('Speech input unavailable')
      isSpeechRecordingRef.current = false
      setIsSpeechRecording(false)
    }
  }

  const stopSpeechRecognition = () => {
    if (!recognitionRef.current || !isSpeechRecordingRef.current) return
    stopRequestedRef.current = true
    try {
      recognitionRef.current.stop()
    } catch (error) {
      console.debug('[speech] stop error', error)
    }
    recognitionRef.current = null
    isSpeechRecordingRef.current = false
    setIsSpeechRecording(false)
    setSpeechStatus('Recording stopped')
  }

  const clearAnswer = () => {
    setAnswerText('')
    finalizedTranscriptRef.current = ''
    interimTranscriptRef.current = ''
    answerBaseRef.current = ''
    setSpeechError('')
    setSpeechStatus('')
  }

  const startMedia = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMediaSupported(false)
      setMediaError('Camera and microphone are not supported in this browser.')
      setMediaStatus('Unsupported browser')
      return null
    }

    if (mediaStream) {
      return mediaStream
    }

    setMediaSupported(true)
    setMediaInitializing(true)
    setMediaError('')
    setMediaStatus('Requesting camera and microphone permission...')

    let stream = null
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
    } catch (error) {
      const devices = await navigator.mediaDevices.enumerateDevices().catch(() => [])
      const hasAudioInput = devices.some((device) => device.kind === 'audioinput')
      const hasVideoInput = devices.some((device) => device.kind === 'videoinput')

      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError' || error.name === 'NotAllowedError') {
        setMediaError('Camera and microphone permission denied.')
        setMediaStatus('Permission denied')
      } else if (error.name === 'NotFoundError' || error.name === 'OverconstrainedError' || error.name === 'DevicesNotFoundError') {
        if (!hasAudioInput && !hasVideoInput) {
          setMediaError('No camera or microphone found.')
          setMediaStatus('No devices found')
        } else if (!hasVideoInput) {
          setMediaError('No camera found.')
          setMediaStatus('No camera')
        } else if (!hasAudioInput) {
          setMediaError('No microphone found.')
          setMediaStatus('No microphone')
        } else {
          setMediaError('Unable to access camera and microphone.')
          setMediaStatus('Media initialization failed')
        }

        const partialStream = new MediaStream()
        try {
          if (hasAudioInput) {
            const audioOnly = await navigator.mediaDevices.getUserMedia({ audio: true })
            audioOnly.getAudioTracks().forEach((track) => partialStream.addTrack(track))
          }
        } catch (audioError) {
          // ignore partial audio fallback
        }
        try {
          if (hasVideoInput) {
            const videoOnly = await navigator.mediaDevices.getUserMedia({ video: true })
            videoOnly.getVideoTracks().forEach((track) => partialStream.addTrack(track))
          }
        } catch (videoError) {
          // ignore partial video fallback
        }

        stream = partialStream.getTracks().length ? partialStream : null
      } else {
        setMediaError('Unable to initialize camera and microphone.')
        setMediaStatus('Media initialization failed')
      }
    }

    if (!stream) {
      setMediaInitializing(false)
      return null
    }

    const audioTracks = stream.getAudioTracks()
    const videoTracks = stream.getVideoTracks()
    setMediaStream(stream)
    setMediaStatus('Media ready')
    setIsRecordingState(true)
    setIsMuted(!audioTracks.length || !audioTracks.some((track) => track.enabled))
    setIsCameraOn(videoTracks.length > 0 && videoTracks.some((track) => track.enabled))
    attachVideo(stream)
    setMediaInitializing(false)
    return stream
  }

  const stopMedia = () => {
    try {
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop())
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    } catch (e) {
      // ignore
    }
    setMediaStream(null)
    setIsRecordingState(false)
    setIsCameraOn(false)
    setIsMuted(false)
    setMediaInitializing(false)
  }

  const attachVideo = (stream) => {
    if (videoRef.current) {
      try {
        videoRef.current.srcObject = stream
        videoRef.current.play().catch(() => {})
      } catch (e) {
        // ignore
      }
    }
  }

  const toggleMute = () => {
    if (!mediaStream) return
    const audioTracks = mediaStream.getAudioTracks()
    if (!audioTracks.length) return
    audioTracks.forEach((track) => {
      track.enabled = !track.enabled
    })
    setIsMuted((prev) => !prev)
    setMediaStatus(audioTracks.some((track) => track.enabled) ? 'Microphone ready' : 'Microphone muted')
  }

  const toggleCamera = () => {
    if (!mediaStream) return
    const videoTracks = mediaStream.getVideoTracks()
    if (!videoTracks.length) return
    videoTracks.forEach((track) => {
      track.enabled = !track.enabled
    })
    setIsCameraOn((prev) => !prev)
    setMediaStatus(videoTracks.some((track) => track.enabled) ? 'Camera ready' : 'Camera disabled')
  }

  const setMediaStreamState = (stream) => {
    setMediaStream(stream)
    const audioTracks = stream.getAudioTracks()
    const videoTracks = stream.getVideoTracks()
    setIsMuted(!audioTracks.length || audioTracks.every((track) => !track.enabled))
    setIsCameraOn(videoTracks.length > 0 && videoTracks.some((track) => track.enabled))
  }

  const cameraStatus = (() => {
    if (mediaInitializing) return 'Initializing...'
    if (!mediaSupported) return 'Unsupported'
    if (mediaError && mediaStatus === 'Permission denied') return 'Permission Denied'
    if (mediaError && mediaStatus === 'No camera') return 'No camera'
    if (mediaError && mediaStatus === 'No devices found') return 'Unavailable'
    if (mediaError && mediaStatus === 'Unsupported browser') return 'Unsupported'
    if (mediaError && !mediaStream) return 'Unavailable'
    if (!mediaStream) return 'Unavailable'
    const videoTracks = mediaStream.getVideoTracks()
    if (!videoTracks.length) return 'Unavailable'
    return videoTracks.every((track) => track.enabled) ? 'Ready' : 'Disabled'
  })()

  const microphoneStatus = (() => {
    if (mediaInitializing) return 'Initializing...'
    if (!mediaSupported) return 'Unsupported'
    if (mediaError && mediaStatus === 'Permission denied') return 'Permission Denied'
    if (mediaError && mediaStatus === 'No microphone') return 'No microphone'
    if (mediaError && mediaStatus === 'No devices found') return 'Unavailable'
    if (mediaError && mediaStatus === 'Unsupported browser') return 'Unsupported'
    if (mediaError && !mediaStream) return 'Unavailable'
    if (!mediaStream) return 'Unavailable'
    const audioTracks = mediaStream.getAudioTracks()
    if (!audioTracks.length) return 'Unavailable'
    return audioTracks.some((track) => track.enabled) ? 'Ready' : 'Muted'
  })()

  const isPreviewActive = Boolean(mediaStream && isCameraOn && mediaSupported && !mediaError)

  const startTimer = (seconds) => {
    setTimerRemaining(seconds)
    const expires = Date.now() + seconds * 1000
    setTimerExpiresAt(expires)
    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setTimerRemaining((prev) => {
        if (isPaused) return prev
        if (prev <= 1) {
          clearInterval(timerRef.current)
          timerRef.current = null
          // time's up: end interview
          handleEndLive()
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const handlePause = () => {
    setIsPaused(true)
    // disable submission
  }

  const handleResume = () => {
    setIsPaused(false)
  }

  const handleRepeat = () => {
    // repeat current question via speech synthesis if available, otherwise focus/flash the prompt
    const text = currentQuestion?.text || transcript[transcript.length - 1]?.text || ''
    if (!text) return
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utter = new SpeechSynthesisUtterance(text)
      utter.rate = 0.95
      window.speechSynthesis.speak(utter)
    } else {
      // fallback: append a copy of the question to transcript to redisplay
      const timestamp = new Date().toISOString()
      setTranscript((prev) => [...prev, { speaker: 'AI', text, timestamp }])
    }
  }

  useEffect(() => {
    if (typeof window === 'undefined') return
    const supported = Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
    setSpeechSupported(supported)
    if (!supported) {
      setSpeechStatus('Voice input is not supported in this browser.')
    }

    const storedState = window.sessionStorage.getItem('interview-page-state')
    if (!storedState) return

    try {
      const parsed = JSON.parse(storedState)
      if (parsed.view === 'live' && parsed.sessionData) {
        setView(parsed.view)
        setSessionData(parsed.sessionData)
        setCurrentQuestion(parsed.currentQuestion)
        setTranscript(parsed.transcript || INITIAL_TRANSCRIPT)
        setQuestionNumber(parsed.questionNumber || 1)
        setConfig(parsed.config || INITIAL_CONFIG)
        setSelectedType(parsed.selectedType || TYPES[0])
        setTimerRemaining(parsed.timerRemaining || 0)
        setIsPaused(parsed.isPaused || false)
        setTimerExpiresAt(parsed.timerExpiresAt || null)

        // try to refresh the current question from backend if we have an id
        ;(async () => {
          try {
            if (parsed.currentQuestion?.question_id) {
              const q = await getInterviewQuestion(parsed.currentQuestion.question_id)
              setCurrentQuestion((prev) => ({ ...(prev || {}), ...q }))
            }
          } catch (e) {
            // ignore failures to refresh question
          }

          // attempt to restart media and resume timer if not paused
          try {
            const stream = await startMedia()
            if (stream) attachVideo(stream)
          } catch (e) {}

          if (!parsed.isPaused) {
            // if we have an expiresAt, compute remaining
            if (parsed.timerExpiresAt) {
              const rem = Math.max(0, Math.round((parsed.timerExpiresAt - Date.now()) / 1000))
              startTimer(rem)
            } else if (parsed.timerRemaining) {
              startTimer(parsed.timerRemaining)
            }
          }
        })()
      }
    } catch (error) {
      console.error('Unable to restore interview state', error)
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const payload = {
      view,
      selectedType,
      config,
      transcript,
      sessionData,
      currentQuestion,
      questionNumber,
      timerRemaining,
      timerExpiresAt,
      isPaused,
    }
    window.sessionStorage.setItem('interview-page-state', JSON.stringify(payload))
  }, [view, selectedType, config, transcript, sessionData, currentQuestion, questionNumber])

  useEffect(() => {
    answerRef.current = answerText
  }, [answerText])

  const startConfiguration = (type) => {
    setSelectedType(type)
    setConfigError('')
    setView('configuration')
  }

  const handleStartDeviceCheck = (values) => {
    const hasRequiredFields = values.role?.trim() && values.companyType?.trim() && values.experience?.trim() && values.duration?.trim() && values.language?.trim() && values.voice?.trim()
    if (!hasRequiredFields) {
      setConfigError('Please complete all fields before continuing.')
      return
    }

    setConfigError('')
    setConfig(values)
    setView('device-check')
  }

  const handleBeginLive = async () => {
    if (isLoading) return

    const requestId = pendingLaunchRef.current + 1
    pendingLaunchRef.current = requestId
    setIsLoading(true)
    setSessionError('')

    try {
      const interviewConfig = {
        interview_type: selectedType.id,
        role: config.role,
        experience_level: config.experience,
        company_type: config.companyType,
        duration: config.duration,
        language: config.language,
      }

      const sessionResponse = await createInterviewSession({
        interviewConfig,
        persona: { tone: 'neutral', strictness: 'balanced' },
      })

      if (pendingLaunchRef.current !== requestId) return

      const now = new Date().toISOString()
      setSessionData(sessionResponse)
      setCurrentQuestion(sessionResponse.question || null)
      setTranscript([{ speaker: 'AI', text: sessionResponse.question?.text || 'Let’s begin.', timestamp: now }])
      setQuestionNumber(1)
      setAnswerText('')
      setSubmissionError('')
      // start media (prompt permission) and attach preview
      try {
        const stream = await startMedia()
        if (stream) attachVideo(stream)
      } catch (e) {
        // media permission denied or unavailable; candidate preview will remain placeholder
      }
      // start timer from backend source of truth when provided
      const duration = (sessionResponse?.timer?.duration_seconds ?? sessionResponse?.timer?.duration) || 1800
      startTimer(Number(duration) || 1800)
      setIsLoading(false)
      setView('live')
    } catch (error) {
      if (pendingLaunchRef.current !== requestId) return
      setIsLoading(false)
      const detail = error?.response?.data?.message || error?.message || 'Unable to start interview right now.'
      setSessionError(detail)
    }
  }

  const handleSubmitAnswer = async () => {
    if (isSubmitting || !sessionData?.session_id) return
    if (isPaused) {
      setSubmissionError('Interview is paused. Resume to submit your answer.')
      return
    }

    const trimmedAnswer = answerText.trim()
    if (!trimmedAnswer) {
      setSubmissionError('Please enter an answer before submitting.')
      return
    }

    setIsSubmitting(true)
    setSubmissionError('')

    try {
      const turnResponse = await submitInterviewTurn({
        sessionId: sessionData.session_id,
        answer: trimmedAnswer,
        persona: { tone: 'neutral', strictness: 'balanced' },
      })

      const feedbackText = turnResponse?.feedback?.text || 'Thanks. I will keep going.'
      const nextPrompt = turnResponse?.followup?.text || turnResponse?.feedback?.text || 'Let’s continue.'
      const evaluation = turnResponse?.turn_evaluation
      const timestamp = new Date().toISOString()

      const aiMessages = [
        { speaker: 'AI', text: feedbackText, timestamp },
      ]

      if (evaluation) {
        const evaluationLines = [
          `Score: ${evaluation.score}/100`,
          evaluation.verdict ? `Verdict: ${evaluation.verdict.replace('_', ' ')}` : null,
        ]
          .filter(Boolean)
          .join('\n')

        const evaluationBody = [
          evaluationLines,
          evaluation.strengths?.length ? `Strengths:\n- ${evaluation.strengths.join('\n- ')}` : null,
          evaluation.missing_concepts?.length ? `Missing Concepts:\n- ${evaluation.missing_concepts.join('\n- ')}` : null,
          evaluation.weaknesses?.length ? `Weaknesses:\n- ${evaluation.weaknesses.join('\n- ')}` : null,
          evaluation.recommendations?.length ? `Recommendations:\n- ${evaluation.recommendations.join('\n- ')}` : null,
        ]
          .filter(Boolean)
          .join('\n\n')

        if (evaluationBody) {
          aiMessages.push({ speaker: 'AI', text: `AI Evaluation\n\n${evaluationBody}`, timestamp })
        }
      }

      if (nextPrompt && nextPrompt !== feedbackText) {
        aiMessages.push({ speaker: 'AI', text: nextPrompt, timestamp })
      }

      setTranscript((prev) => [
        ...prev,
        { speaker: 'You', text: trimmedAnswer, timestamp },
        ...aiMessages,
      ])
      setCurrentQuestion({ ...(currentQuestion || {}), text: nextPrompt, question_id: turnResponse?.followup?.targets_gap ? undefined : currentQuestion?.question_id })
      setQuestionNumber((prev) => prev + 1)
      setAnswerText('')
    } catch (error) {
      const detail = error?.response?.data?.message || error?.message || 'Unable to submit your answer right now.'
      setSubmissionError(detail)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEndLive = async () => {
    if (!sessionData?.session_id) {
      // No active session — just return to home
      setSessionError('No active interview session found.')
      setView('home')
      return
    }
    // stop local media and timers, but do NOT invoke report generation per instructions
    stopTimer()
    try {
      if (window.speechSynthesis) window.speechSynthesis.cancel()
    } catch (e) {}
    stopMedia()
    setIsRecordingState(false)
    setTimerRemaining(0)
    setSessionData(null)
    setCurrentQuestion(null)
    setTranscript(INITIAL_TRANSCRIPT)
    setView('home')
  }

  const goHome = () => {
    cancelPendingLaunch()
    setReportData(null)
    setReportError('')
    setView('home')
  }

  const goDashboard = () => {
    navigate('/dashboard')
  }

  const backHandlers = useMemo(
    () => ({
      configuration: () => {
        cancelPendingLaunch()
        setView('home')
      },
      'device-check': () => {
        cancelPendingLaunch()
        setView('configuration')
      },
      live: () => {
        cancelPendingLaunch()
        setView('device-check')
      },
      report: () => {
        cancelPendingLaunch()
        setView('home')
      },
      history: () => {
        cancelPendingLaunch()
        setView('home')
      },
    }),
    []
  )

  useEffect(() => {
    if (mediaStream) attachVideo(mediaStream)
  }, [mediaStream])

  useEffect(() => {
    return () => {
      stopRequestedRef.current = true
      if (autoRestartTimerRef.current) {
        window.clearTimeout(autoRestartTimerRef.current)
      }
      stopSpeechRecognition()
      stopTimer()
      stopMedia()
    }
  }, [])

  return (
    <InterviewLayout title="AI Interview" intro="Practice realistic interviews with clear feedback and calm structure." showBack={view !== 'home'} onBack={backHandlers[view]}>
      {view === 'home' && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">Placement preparation</p>
                <h3 className="text-xl font-semibold text-white">Practice interviews that feel close to the real thing.</h3>
              </div>
              <button onClick={() => setView('history')} className="rounded-2xl border border-slate-800 px-3 py-2 text-sm font-semibold text-slate-100">Review history</button>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {TYPES.map((type) => (
              <InterviewTypeCard
                key={type.id}
                icon={type.icon}
                title={type.title}
                description={type.description}
                duration={type.duration}
                onStart={() => startConfiguration(type)}
              />
            ))}
          </div>
        </div>
      )}

      {view === 'configuration' && (
        <div className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-800 bg-slate-950/80 p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm text-slate-400">Interview configuration</p>
              <h3 className="text-xl font-semibold text-white">{selectedType.title}</h3>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-300">{selectedType.duration}</div>
          </div>
          {configError && (
            <div className="mb-4 rounded-2xl border border-amber-800 bg-amber-950/50 p-3 text-sm text-amber-200">
              {configError}
            </div>
          )}
          <ConfigurationForm
            values={config}
            onChange={(e) => setConfig((prev) => ({ ...prev, [e.target.name]: e.target.value }))}
            onSubmit={(e) => {
              e.preventDefault()
              handleStartDeviceCheck(config)
            }}
          />
        </div>
      )}

      {view === 'device-check' && (
        <div className="mx-auto w-full max-w-3xl">
          <DeviceCheck onBegin={handleBeginLive} isStarting={isLoading} />
          {sessionError && (
            <div className="mt-4 rounded-2xl border border-rose-800 bg-rose-950/50 p-3 text-sm text-rose-200">
              {sessionError}
            </div>
          )}
          {isLoading && (
            <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/80 p-3 text-sm text-slate-300">
              Starting your interview session...
            </div>
          )}
        </div>
      )}

      {view === 'live' && (
        <div className="grid gap-6 xl:grid-cols-[1.25fr_0.8fr]">
          <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Live interview</p>
                <h3 className="text-xl font-semibold text-white">{selectedType.title}</h3>
              </div>
              <div className="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-sm text-slate-300">{Math.floor((timerRemaining || 0) / 60).toString().padStart(2, '0')}:{String((timerRemaining || 0) % 60).padStart(2, '0')}</div>
            </div>
            <QuestionCard
              title="Current question"
              prompt={currentQuestion?.text || 'Loading your first question...'}
              timer={`${Math.floor((timerRemaining || 0) / 60).toString().padStart(2, '0')}:${String((timerRemaining || 0) % 60).padStart(2, '0')}`}
              questionNumber={questionNumber}
            />
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <label className="text-sm font-medium text-slate-200" htmlFor="answer-input">Your answer</label>
              <textarea
                id="answer-input"
                rows="5"
                value={answerText}
                onChange={(event) => setAnswerText(event.target.value)}
                disabled={isSubmitting}
                placeholder="Type your answer here. The backend interview engine will evaluate it and return the next prompt."
                className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none disabled:cursor-not-allowed disabled:opacity-60"
              />
              <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
                <button
                  type="button"
                  onClick={startSpeechRecognition}
                  disabled={!speechSupported || isSpeechRecording || isSubmitting}
                  className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  🎤 Start Recording
                </button>
                {isSpeechRecording && (
                  <button
                    type="button"
                    onClick={stopSpeechRecognition}
                    disabled={!isSpeechRecording || isSubmitting}
                    className="rounded-2xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    ⏹ Stop Recording
                  </button>
                )}
                <button
                  type="button"
                  onClick={clearAnswer}
                  disabled={isSubmitting}
                  className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-semibold text-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  🗑 Clear
                </button>
              </div>
              <div className="mt-3 rounded-2xl border border-slate-800 bg-slate-950/80 px-3 py-3 text-sm text-slate-200">
                {speechStatus && <p className="text-slate-200">{speechStatus}</p>}
                {speechError && <p className="mt-1 text-rose-300">{speechError}</p>}
                {!speechSupported && !speechStatus && <p className="text-slate-400">Voice input is not supported in this browser.</p>}
              </div>
              {submissionError && (
                <div className="mt-3 rounded-2xl border border-rose-800 bg-rose-950/50 p-3 text-sm text-rose-200">
                  {submissionError}
                </div>
              )}
            </div>
            <TranscriptPanel transcript={transcript} />
          </div>

          <div className="space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Candidate preview</p>
                  <h3 className="text-lg font-semibold text-white">Ready to speak</h3>
                </div>
                <RecordingIndicator isRecording={isRecordingState} isPaused={isPaused} isMuted={isMuted} isConnected={navigator.onLine} statusText={isSubmitting ? 'Processing' : ''} />
              </div>

              <div className="mt-5 flex aspect-video items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/70 text-slate-500">
                {isPreviewActive ? (
                  <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
                ) : (
                  <div className="text-center w-full px-4">
                    <div className="mb-3 flex justify-center">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10 text-accent">
                        <Monitor size={20} />
                      </div>
                    </div>
                    <p className="text-sm font-medium text-slate-100">
                      {mediaInitializing
                        ? 'Initializing camera preview...'
                        : mediaError
                        ? mediaError
                        : !mediaSupported
                        ? 'Voice and camera are not supported in this browser.'
                        : !mediaStream
                        ? 'No camera stream available.'
                        : !isCameraOn
                        ? 'Camera is disabled. Enable it to see live preview.'
                        : 'Camera preview unavailable.'}
                    </p>
                    {mediaStream && !isCameraOn && (
                      <p className="mt-2 text-xs text-slate-400">Use the camera toggle to restore the live preview.</p>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-4 grid gap-2 text-sm text-slate-300">
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2"><span>Microphone</span><span className="text-slate-400">{microphoneStatus}</span></div>
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2"><span>Camera</span><span className="text-slate-400">{cameraStatus}</span></div>
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2"><span>Connection</span><span className="text-slate-400">{navigator.onLine ? 'Stable' : 'Offline'}</span></div>
              </div>
            </div>

            <InterviewControls
              isMuted={isMuted}
              isCameraOn={isCameraOn}
              onMute={toggleMute}
              onCamera={toggleCamera}
              onSubmit={handleSubmitAnswer}
              isSubmitting={isSubmitting}
              canSubmit={!isLoading && !isPaused}
              onEnd={handleEndLive}
              onPause={handlePause}
              onResume={handleResume}
              onRepeat={handleRepeat}
              isPaused={isPaused}
            />
          </div>
        </div>
      )}

      {view === 'report' && (
        <div className="space-y-4">
          {isReportLoading ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 text-sm text-slate-400">Generating your report...</div>
          ) : reportError ? (
            <div className="rounded-2xl border border-rose-800 bg-rose-950/50 p-5 text-sm text-rose-200">{reportError}</div>
          ) : reportData ? (
            <ReportCard
              score={reportData.overall_score}
              summary={reportData.summary}
              strengths={reportData.strengths}
              improvements={reportData.weaknesses}
              communication={reportData.communication_score ? `Communication score: ${reportData.communication_score}/100` : 'Communication feedback available in the report.'}
              technical={reportData.technical_score ? `Technical score: ${reportData.technical_score}/100` : 'Technical feedback available in the report.'}
              topics={reportData.recommendations || []}
            />
          ) : (
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 text-sm text-slate-400">No report available yet. Please complete the interview session.</div>
          )}

          <div className="flex flex-wrap gap-3">
            <button onClick={goHome} className="rounded-2xl border border-slate-800 px-4 py-2 text-sm font-semibold text-slate-100">Practice again</button>
            <button onClick={goDashboard} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">Back to Dashboard</button>
          </div>
        </div>
      )}

      {view === 'history' && (
        <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-slate-400">Interview history</p>
              <h3 className="text-xl font-semibold text-white">Your recent sessions</h3>
            </div>
            <div className="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-300">
              <Sparkles size={16} className="text-accent" />
              Search and filter ready
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none" placeholder="Search interview history" />
            <button className="rounded-2xl border border-slate-800 px-3 py-2 text-sm text-slate-100">Filter</button>
          </div>

          <HistoryTable rows={HISTORY_ROWS} onOpen={() => setView('report')} />
        </div>
      )}
    </InterviewLayout>
  )
}
