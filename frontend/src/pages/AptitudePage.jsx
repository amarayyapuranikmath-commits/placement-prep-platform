import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import InstructionCard from '../components/aptitude/InstructionCard'
import ConfigurationForm from '../components/aptitude/ConfigurationForm'
import QuestionCard from '../components/aptitude/QuestionCard'
import QuestionPalette from '../components/aptitude/QuestionPalette'
import TimerDisplay from '../components/aptitude/TimerDisplay'
import NavigationControls from '../components/aptitude/NavigationControls'
import ResultCard from '../components/aptitude/ResultCard'
import ReviewAnswerCard from '../components/aptitude/ReviewAnswerCard'
import EmptyState from '../components/aptitude/EmptyState'
import LoadingSkeleton from '../components/aptitude/LoadingSkeleton'
import {
  clearAptitudeAnswer,
  createAptitudeSession,
  getAptitudeHistory,
  getAptitudeResult,
  getAptitudeReview,
  getAptitudeSession,
  saveAptitudeAnswer,
  submitAptitudeSession,
} from '../services/aptitudeApi'

const VIEWS = {
  HOME: 'home',
  INSTRUCTIONS: 'instructions',
  CONFIG: 'config',
  TEST: 'test',
  RESULT: 'result',
  REVIEW: 'review',
  HISTORY: 'history',
}

const DEFAULT_CONFIG = {
  testType: 'Quantitative Aptitude',
  difficulty: 'Easy',
  questionCount: 10,
}

const getTotalTestSeconds = (questionCount) => Math.max(0, Number(questionCount || 0) * 60)

export default function AptitudePage() {
  const navigate = useNavigate()
  const [view, setView] = useState(VIEWS.HOME)
  const [config, setConfig] = useState(DEFAULT_CONFIG)
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [reviewFlags, setReviewFlags] = useState({})
  const [resultSummary, setResultSummary] = useState(null)
  const [reviewItems, setReviewItems] = useState([])
  const [reviewIndex, setReviewIndex] = useState(0)
  const [historyItems, setHistoryItems] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [timerSeconds, setTimerSeconds] = useState(0)
  const [timerConfig, setTimerConfig] = useState({ duration_seconds: 0, started_at: null })
  const timerExpiredRef = useRef(false)

  const normalizeDifficulty = (value) => {
    if (!value) return 'Easy'
    return value[0].toUpperCase() + value.slice(1).toLowerCase()
  }

  const mapStoredAnswers = (rawAnswers) =>
    Object.fromEntries(
      Object.entries(rawAnswers || {}).map(([questionId, value]) => [questionId, value?.answer ?? null]),
    )

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainder = seconds % 60
    return `${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`
  }

  const getRemainingSeconds = (timer) => {
    if (!timer) return 0
    const duration = Number(timer.duration_seconds ?? 0)
    const startedAt = timer.started_at ? new Date(timer.started_at) : null
    if (!startedAt || Number.isNaN(startedAt.getTime())) return duration
    const elapsed = Math.floor((Date.now() - startedAt.getTime()) / 1000)
    return Math.max(duration - elapsed, 0)
  }

  const formatHistoryDate = (submittedAt) => {
    if (!submittedAt) return 'Unknown date'
    const date = new Date(submittedAt)
    if (Number.isNaN(date.getTime())) return 'Invalid date'
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const initializeTimer = (timerPayload, questionCount = config.questionCount || DEFAULT_CONFIG.questionCount) => {
    const durationSeconds = Number(timerPayload?.duration_seconds ?? getTotalTestSeconds(questionCount))
    const fallbackDuration = getTotalTestSeconds(questionCount)
    const remainingSeconds = timerPayload ? Math.min(getRemainingSeconds(timerPayload), fallbackDuration || durationSeconds) : fallbackDuration
    setTimerConfig({ duration_seconds: durationSeconds || fallbackDuration, started_at: timerPayload?.started_at ?? new Date().toISOString() })
    setTimerSeconds(remainingSeconds)
  }

  const moveToQuestion = (nextIndex) => {
    if (nextIndex < 0 || nextIndex >= questions.length) return
    setCurrentIndex(nextIndex)
  }

  const resetAptitudeState = () => {
    setQuestions([])
    setCurrentIndex(0)
    setAnswers({})
    setReviewFlags({})
    setResultSummary(null)
    setReviewItems([])
    setReviewIndex(0)
    setSessionId(null)
    timerExpiredRef.current = false
    setTimerSeconds(0)
    setTimerConfig({ duration_seconds: 0, started_at: null })
    setErrorMessage('')
  }

  const clearStoredSession = () => {
    localStorage.removeItem('aptitude_session_id')
  }

  const startAptitudeSession = async (overrideConfig = config) => {
    setIsLoading(true)
    setErrorMessage('')
    clearStoredSession()
    resetAptitudeState()
    setView(VIEWS.TEST)

    try {
      const payload = {
        test_type: overrideConfig.testType,
        difficulty: overrideConfig.difficulty.toLowerCase(),
        question_count: overrideConfig.questionCount,
      }
      const data = await createAptitudeSession(payload)
      setSessionId(data.session_id)
      localStorage.setItem('aptitude_session_id', data.session_id)
      setConfig({
        testType: data.test_metadata?.test_type ?? overrideConfig.testType,
        difficulty: normalizeDifficulty(data.test_metadata?.difficulty ?? overrideConfig.difficulty),
        questionCount: data.test_metadata?.question_count ?? overrideConfig.questionCount,
      })
      const nextQuestions = data.questions || []
      const totalSeconds = getTotalTestSeconds(nextQuestions.length || overrideConfig.questionCount || config.questionCount)
      setQuestions(nextQuestions)
      setCurrentIndex(0)
      setAnswers({})
      setReviewFlags({})
      setResultSummary(null)
      setReviewIndex(0)
      setTimerSeconds(totalSeconds)
      setTimerConfig({ duration_seconds: totalSeconds, started_at: new Date().toISOString() })
      timerExpiredRef.current = false
      setView(VIEWS.TEST)
    } catch (error) {
      setSessionId(null)
      clearStoredSession()
      setErrorMessage(error?.response?.data?.message || 'Unable to start the aptitude test right now.')
      setView(VIEWS.CONFIG)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartTest = async () => {
    await startAptitudeSession()
  }

  const handleCreateNewTest = async () => {
    await startAptitudeSession()
  }

  const handleBackToHome = () => {
    clearStoredSession()
    resetAptitudeState()
    setView(VIEWS.HOME)
  }

  const handleExitTest = () => {
    const hasProgress = Object.keys(answers).length > 0 || Object.keys(reviewFlags).length > 0
    if (hasProgress) {
      const confirmExit = window.confirm(
        'You are currently in a live test. Leaving now may interrupt your progress. Do you want to continue?',
      )
      if (!confirmExit) {
        return
      }
    }
    setView(VIEWS.INSTRUCTIONS)
  }

  const currentQuestion = questions[currentIndex]
  const reviewQuestion = reviewItems[reviewIndex] || questions[reviewIndex]
  const timerValue = formatDuration(timerSeconds)

  const paletteItems = useMemo(
    () =>
      questions.map((question) => ({
        id: question.id,
        status: answers[question.id]
          ? reviewFlags[question.id]
            ? 'review'
            : 'answered'
          : 'unanswered',
      })),
    [questions, answers, reviewFlags],
  )

  const handleSubmitTest = useCallback(async () => {
    if (!sessionId) return
    setIsLoading(true)
    setErrorMessage('')
    try {
      const data = await submitAptitudeSession(sessionId)
      setResultSummary({
        score: `${data.summary.score}`,
        correctAnswers: data.summary.correct,
        incorrectAnswers: data.summary.incorrect,
        unanswered: data.summary.unanswered,
        accuracy: `${data.summary.accuracy}%`,
        timeTaken: `${Math.floor(data.summary.time_taken_seconds / 60)}m ${data.summary.time_taken_seconds % 60}s`,
      })
      setView(VIEWS.RESULT)
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to submit the aptitude test right now.')
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  useEffect(() => {
    if (view !== VIEWS.TEST || !sessionId || timerExpiredRef.current || timerSeconds <= 0) return undefined

    const interval = window.setInterval(() => {
      setTimerSeconds((prevSeconds) => {
        if (prevSeconds <= 1) {
          timerExpiredRef.current = true
          window.clearInterval(interval)
          void handleSubmitTest()
          return 0
        }

        return prevSeconds - 1
      })
    }, 1000)

    return () => window.clearInterval(interval)
  }, [view, sessionId, handleSubmitTest])

  useEffect(() => {
    const restoreSession = async () => {
      const storedSessionId = localStorage.getItem('aptitude_session_id')
      if (!storedSessionId) return

      setIsLoading(true)
      setErrorMessage('')
      try {
        const session = await getAptitudeSession(storedSessionId)
        setSessionId(session.session_id)
        setConfig({
          testType: session.test_type,
          difficulty: normalizeDifficulty(session.difficulty),
          questionCount: session.question_count,
        })
        setQuestions(session.questions || [])
        setAnswers(mapStoredAnswers(session.answers))
        setReviewFlags(session.review_flags || {})
        setCurrentIndex(0)
        setReviewIndex(0)
        initializeTimer(session.timer)

        if (session.status === 'completed') {
          const result = await getAptitudeResult(storedSessionId)
          setResultSummary({
            score: `${result.summary.score}`,
            correctAnswers: result.summary.correct,
            incorrectAnswers: result.summary.incorrect,
            unanswered: result.summary.unanswered,
            accuracy: `${result.summary.accuracy}%`,
            timeTaken: `${Math.floor(result.summary.time_taken_seconds / 60)}m ${result.summary.time_taken_seconds % 60}s`,
          })
          setView(VIEWS.RESULT)
        } else {
          setView(VIEWS.TEST)
        }
      } catch (error) {
        localStorage.removeItem('aptitude_session_id')
        setErrorMessage(error?.response?.data?.message || 'Unable to restore your aptitude session.')
      } finally {
        setIsLoading(false)
      }
    }

    restoreSession()
  }, [])


  const handleReviewAnswers = async () => {
    if (!sessionId) return
    setIsLoading(true)
    setErrorMessage('')
    try {
      const data = await getAptitudeReview(sessionId)
      setReviewItems(data.questions || [])
      setReviewIndex(0)
      setAnswers(
        Object.fromEntries(
          (data.questions || []).map((item) => [item.question_id, item.user_answer]),
        ),
      )
      setView(VIEWS.REVIEW)
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to load review answers right now.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleOpenHistory = async (historySessionId) => {
    setIsLoading(true)
    setErrorMessage('')
    try {
      const result = await getAptitudeResult(historySessionId)
      setSessionId(historySessionId)
      setResultSummary({
        score: `${result.summary.score}`,
        correctAnswers: result.summary.correct,
        incorrectAnswers: result.summary.incorrect,
        unanswered: result.summary.unanswered,
        accuracy: `${result.summary.accuracy}%`,
        timeTaken: `${Math.floor(result.summary.time_taken_seconds / 60)}m ${result.summary.time_taken_seconds % 60}s`,
      })
      setReviewItems([])
      setReviewIndex(0)
      setView(VIEWS.RESULT)
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to load history result right now.')
    } finally {
      setIsLoading(false)
    }
  }

  const loadHistory = async () => {
    setHistoryLoading(true)
    setErrorMessage('')
    try {
      const history = await getAptitudeHistory()
      setHistoryItems(history)
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to load aptitude history right now.')
    } finally {
      setHistoryLoading(false)
    }
  }

  useEffect(() => {
    if (view === VIEWS.HOME || view === VIEWS.HISTORY) {
      loadHistory()
    }
  }, [view])

  const handleAnswerSelect = async (value) => {
    if (!currentQuestion || !sessionId) return
    const nextAnswers = { ...answers, [currentQuestion.question_id]: value }
    setAnswers(nextAnswers)
    try {
      await saveAptitudeAnswer(sessionId, currentQuestion.question_id, { answer: value, review: reviewFlags[currentQuestion.question_id] || false })
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to save your answer right now.')
    }
  }

  const handleToggleReview = async () => {
    if (!currentQuestion || !sessionId) return
    const nextReview = !reviewFlags[currentQuestion.question_id]
    setReviewFlags((prev) => ({ ...prev, [currentQuestion.question_id]: nextReview }))
    try {
      await saveAptitudeAnswer(sessionId, currentQuestion.question_id, { review: nextReview })
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to update review state right now.')
    }
  }

  const handleClearAnswer = async () => {
    if (!currentQuestion || !sessionId) return
    const next = { ...answers }
    delete next[currentQuestion.question_id]
    setAnswers(next)
    try {
      await clearAptitudeAnswer(sessionId, currentQuestion.question_id)
    } catch (error) {
      setErrorMessage(error?.response?.data?.message || 'Unable to clear the answer right now.')
    }
  }

  const handleReviewNavigation = (direction) => {
    setReviewIndex((prev) => {
      const maxIndex = (reviewItems.length > 0 ? reviewItems.length : questions.length) - 1
      const next = direction === 'next' ? prev + 1 : prev - 1
      return Math.max(0, Math.min(next, maxIndex))
    })
  }

  if (view === VIEWS.HOME) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <section className="rounded-3xl border border-slate-800 bg-slate-950/90 p-8 shadow-sm">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
          <h1 className="mt-4 text-3xl font-semibold text-white">Aptitude</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-400">
            Practice placement aptitude questions and improve your problem-solving skills.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">
              <p className="text-sm font-medium text-slate-100">Start Aptitude Test</p>
              <p className="mt-2 text-sm text-slate-400">A clean, guided practice experience for your next placement test.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => setView(VIEWS.INSTRUCTIONS)}
                className="inline-flex items-center justify-center rounded-2xl bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
              >
                Start
              </button>
              <button
                type="button"
                onClick={() => setView(VIEWS.HISTORY)}
                className="inline-flex items-center justify-center rounded-2xl border border-slate-800 bg-slate-950/90 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
              >
                View History
              </button>
            </div>
          </div>
        </section>
      </div>
    )
  }

  if (view === VIEWS.INSTRUCTIONS) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setView(VIEWS.HOME)}
            className="rounded-2xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
          >
            Back to Home
          </button>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
        </div>

        <div className="space-y-3">
          <h1 className="text-3xl font-semibold text-white">Instructions</h1>
          <p className="max-w-2xl text-sm text-slate-400">
            Review the test format before you begin so you can stay focused and complete the assessment efficiently.
          </p>
        </div>

        <InstructionCard
          title="Aptitude assessment overview"
          description="This session is designed as a focused practice test with a clean interface and clear navigation."
          items={[
            { title: 'Duration', detail: '10 questions with 60 seconds per question, resetting as you move through the test.' },
            { title: 'Question Pattern', detail: 'Multiple-choice questions covering aptitude fundamentals.' },
            { title: 'Navigation Instructions', detail: 'Use the controls to move between questions and track progress.' },
            { title: 'Mark for Review', detail: 'Flag questions you want to revisit before submission.' },
            { title: 'Auto Submit on Timer End', detail: 'The final question auto-submits when the 60-second countdown expires.' },
          ]}
        />

        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => setView(VIEWS.CONFIG)}
            className="inline-flex items-center justify-center rounded-2xl bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
          >
            Continue
          </button>
        </div>
      </div>
    )
  }

  if (view === VIEWS.CONFIG) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setView(VIEWS.INSTRUCTIONS)}
            className="rounded-2xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
          >
            Back to Instructions
          </button>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
        </div>

        <div className="space-y-3">
          <h1 className="text-3xl font-semibold text-white">Test configuration</h1>
          <p className="max-w-2xl text-sm text-slate-400">
            Select the test type, difficulty level, and the number of questions for your practice session.
          </p>
        </div>
        {errorMessage ? <p className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">{errorMessage}</p> : null}
        <ConfigurationForm
          config={config}
          onChange={(field, value) => setConfig((prev) => ({ ...prev, [field]: value }))}
          onSubmit={handleStartTest}
        />
      </div>
    )
  }

  if (view === VIEWS.TEST) {
    return (
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="space-y-2">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude Assessment</p>
            <h1 className="text-3xl font-semibold text-white">{config.testType}</h1>
            <p className="max-w-2xl text-sm text-slate-400">Answer the questions below and submit when you are ready. The sidebar shows your question status.</p>
          </div>
          <div className="rounded-3xl border border-slate-800 bg-slate-950/90 px-5 py-4 text-sm text-slate-300">
            <p className="font-medium text-slate-100">Question {currentIndex + 1} of {questions.length}</p>
            <p className="mt-1">Difficulty: {config.difficulty}</p>
          </div>
        </div>

        {isLoading ? (
          <LoadingSkeleton />
        ) : (
          <div className="grid gap-6 xl:grid-cols-[1.5fr_0.9fr]">
            <div className="space-y-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <TimerDisplay label="Timer" value={timerValue} />
                <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-5">
                  <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Current question</p>
                  <p className="mt-3 text-sm text-slate-400">Choose the best answer from the options below. Use review to flag items before submitting.</p>
                </div>
              </div>

              {errorMessage ? <p className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">{errorMessage}</p> : null}
              {currentQuestion ? (
                <QuestionCard
                  question={currentQuestion}
                  selectedAnswer={answers[currentQuestion.question_id]}
                  onSelectAnswer={handleAnswerSelect}
                />
              ) : (
                <EmptyState
                  title="No questions available"
                  subtitle="This test does not have any questions configured yet."
                  actionLabel="Back to configuration"
                  onAction={() => setView(VIEWS.CONFIG)}
                />
              )}

              <NavigationControls
                onPrevious={() => moveToQuestion(Math.max(currentIndex - 1, 0))}
                onNext={() => moveToQuestion(Math.min(currentIndex + 1, questions.length - 1))}
                onMark={handleToggleReview}
                onClear={handleClearAnswer}
                onSubmit={handleSubmitTest}
                disablePrevious={currentIndex === 0}
                disableNext={currentIndex === questions.length - 1}
              />
            </div>

            <aside className="hidden xl:block">
              <QuestionPalette
                items={paletteItems}
                currentIndex={currentIndex}
                onSelect={setCurrentIndex}
              />
            </aside>
          </div>
        )}
      </div>
    )
  }

  if (view === VIEWS.RESULT) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
          <h1 className="text-3xl font-semibold text-white">Result summary</h1>
          <p className="max-w-2xl text-sm text-slate-400">Review your mock test metrics and continue to review answers or return to the dashboard.</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <ResultCard label="Overall score" value={`${resultSummary.score}%`} note="Mock performance summary" />
          <ResultCard label="Correct answers" value={resultSummary.correctAnswers} />
          <ResultCard label="Incorrect answers" value={resultSummary.incorrectAnswers} />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <ResultCard label="Unanswered" value={resultSummary.unanswered} />
          <ResultCard label="Accuracy" value={resultSummary.accuracy} />
          <ResultCard label="Time taken" value={resultSummary.timeTaken} />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleReviewAnswers}
              className="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:bg-slate-800"
            >
              Review Answers
            </button>
            <button
              type="button"
              onClick={handleCreateNewTest}
              className="rounded-2xl bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
            >
              Start New Test
            </button>
            <button
              type="button"
              onClick={handleCreateNewTest}
              className="rounded-2xl border border-slate-800 bg-slate-950/90 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
            >
              Retake Test
            </button>
          </div>
          <button
            type="button"
            onClick={handleBackToHome}
            className="rounded-2xl border border-slate-800 bg-slate-950/90 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  if (view === VIEWS.REVIEW) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
          <h1 className="text-3xl font-semibold text-white">Review answers</h1>
          <p className="max-w-2xl text-sm text-slate-400">Navigate through your responses and compare them with the correct answers.</p>
        </div>

        {reviewItems.length > 0 ? (
          <div className="space-y-6">
            <ReviewAnswerCard
              question={reviewQuestion}
              selectedAnswer={answers[reviewQuestion.question_id]}
              correctAnswer={reviewQuestion.correct_answer || reviewQuestion.correctOption}
              explanation={reviewQuestion.explanation}
              isCorrect={answers[reviewQuestion.question_id] === (reviewQuestion.correct_answer || reviewQuestion.correctOption)}
            />

            <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => handleReviewNavigation('prev')}
                  disabled={reviewIndex === 0}
                  className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => handleReviewNavigation('next')}
                  disabled={reviewIndex === (reviewItems.length > 0 ? reviewItems.length : questions.length) - 1}
                  className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Next
                </button>
              </div>
              <button
                type="button"
                onClick={() => setView(VIEWS.RESULT)}
                className="rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
              >
                Back to Results
              </button>
            </div>
          </div>
        ) : (
          <EmptyState
            title="Nothing to review"
            subtitle="No questions are available for review yet."
            actionLabel="Go back to results"
            onAction={() => setView(VIEWS.RESULT)}
          />
        )}
      </div>
    )
  }

  if (view === VIEWS.HISTORY) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Aptitude</p>
          <h1 className="text-3xl font-semibold text-white">History</h1>
          <p className="max-w-2xl text-sm text-slate-400">View your completed aptitude test results and reopen them.</p>
        </div>

        {historyLoading ? (
          <LoadingSkeleton />
        ) : historyItems.length > 0 ? (
          <div className="grid gap-4">
            {historyItems.map((item) => (
              <div key={item.session_id} className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-sm">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-slate-400">{item.test_type} • {normalizeDifficulty(item.difficulty)}</p>
                    <p className="text-lg font-semibold text-white">{item.summary.score}% score</p>
                  </div>
                  <div className="flex flex-col gap-2 text-right text-sm text-slate-300">
                    <span>{formatHistoryDate(item.submitted_at)}</span>
                    <button
                      type="button"
                      onClick={() => handleOpenHistory(item.session_id)}
                      className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
                    >
                      Open result
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No history yet"
            subtitle="Complete a test to see your history here."
            actionLabel="Back to Home"
            onAction={() => setView(VIEWS.HOME)}
          />
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          <button
            type="button"
            onClick={() => setView(VIEWS.HOME)}
            className="rounded-2xl border border-slate-800 bg-slate-950/90 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-900"
          >
            Back to Home
          </button>
          <button
            type="button"
            onClick={handleCreateNewTest}
            className="rounded-2xl bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
          >
            Start New Test
          </button>
        </div>
      </div>
    )
  }

  return null
}
