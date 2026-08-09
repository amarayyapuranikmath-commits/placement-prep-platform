import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useCodingPreferences } from '../hooks/useCodingPreferences'
import { useProblemWorkspace } from '../hooks/useProblemWorkspace'
import { getProblemDetail, getProblemNeighbors } from '../services/codingService'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import DifficultyBadge from '../components/coding/DifficultyBadge'
import ProblemStatementPanel from '../components/coding/ProblemStatementPanel'
import CodeWorkspace from '../components/coding/CodeWorkspace'
import ConsolePanel from '../components/coding/ConsolePanel'
import SubmissionResultPanel from '../components/coding/SubmissionResultPanel'

const CodingProblemPage = () => {
  const { problemId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { preferredLanguage } = useCodingPreferences()

  const currentFilters = useMemo(() => {
    const query = new URLSearchParams(location.search)

    return {
      search: location.state?.filters?.search ?? query.get('search') ?? '',
      category: location.state?.filters?.category ?? query.get('category') ?? '',
      difficulty: location.state?.filters?.difficulty ?? query.get('difficulty') ?? '',
      language: location.state?.filters?.language ?? query.get('language') ?? '',
      page: location.state?.filters?.page ?? (Number(query.get('page')) || 1),
    }
  }, [location.search, location.state])

  const [neighborState, setNeighborState] = useState({
    previousProblemId: null,
    nextProblemId: null,
    position: 0,
    total: 0,
    isLoading: true,
  })

  const {
    problem,
    isLoading,
    error,
    language,
    changeLanguage,
    code,
    setCode,
    resetCode,
    isRunning,
    runResult,
    runError,
    isSubmitting,
    submitResult,
    submitError,
    handleRun,
    handleSubmit,
  } = useProblemWorkspace(problemId, preferredLanguage)

  useEffect(() => {
    const loadNeighbors = async () => {
      if (!problemId) return

      setNeighborState((previous) => ({
        ...previous,
        isLoading: true,
      }))

      try {
        const neighborData = await getProblemNeighbors({
          problemId,
          search: currentFilters.search,
          category: currentFilters.category,
          difficulty: currentFilters.difficulty,
          language: currentFilters.language,
        })

        setNeighborState({
          previousProblemId: neighborData.previous_problem_id,
          nextProblemId: neighborData.next_problem_id,
          position: neighborData.position,
          total: neighborData.total,
          isLoading: false,
        })
      } catch {
        setNeighborState((previous) => ({
          ...previous,
          isLoading: false,
        }))
      }
    }

    loadNeighbors()
  }, [problemId, currentFilters])

  useEffect(() => {
    const prefetchProblem = async (id) => {
      if (!id) return
      try {
        await getProblemDetail(id)
      } catch {
        // Prefetch best-effort only
      }
    }

    prefetchProblem(neighborState.previousProblemId)
    prefetchProblem(neighborState.nextProblemId)
  }, [neighborState.previousProblemId, neighborState.nextProblemId])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error || !problem) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <ErrorMessage message={error || 'Problem not found'} />
      </div>
    )
  }

  const availableLanguages = Object.keys(problem.starter_code || {})

  const buildCodingListUrl = () => {
    const params = new URLSearchParams()

    if (currentFilters.search) params.set('search', currentFilters.search)
    if (currentFilters.category) params.set('category', currentFilters.category)
    if (currentFilters.difficulty) params.set('difficulty', currentFilters.difficulty)
    if (currentFilters.language) params.set('language', currentFilters.language)
    if (currentFilters.page > 1) params.set('page', String(currentFilters.page))

    const queryString = params.toString()
    return queryString ? `/coding?${queryString}` : '/coding'
  }

  const handleBack = () => {
    navigate(buildCodingListUrl())
  }

  const handleNavigateProblem = (targetProblemId) => {
    if (!targetProblemId) return

    const params = new URLSearchParams()
    if (currentFilters.search) params.set('search', currentFilters.search)
    if (currentFilters.category) params.set('category', currentFilters.category)
    if (currentFilters.difficulty) params.set('difficulty', currentFilters.difficulty)
    if (currentFilters.language) params.set('language', currentFilters.language)
    if (currentFilters.page > 1) params.set('page', String(currentFilters.page))

    const queryString = params.toString()
    navigate(`/coding/${targetProblemId}${queryString ? `?${queryString}` : ''}`, {
      state: {
        filters: currentFilters,
      },
    })
  }

  return (
    <div className="flex h-full flex-col gap-4 p-4 sm:p-6 lg:p-8">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <button
            type="button"
            onClick={handleBack}
            className="mt-1 flex items-center gap-2 text-sm text-slate-400 transition-colors hover:text-slate-100"
          >
            <ArrowLeft size={16} />
            Back
          </button>

          <div>
            <h1 className="text-lg font-semibold text-slate-100 sm:text-xl">
              {problem.title}
            </h1>

            <div className="mt-2 flex items-center gap-2">
              {problem.category && (
                <span className="text-xs text-slate-500">{problem.category}</span>
              )}

              <DifficultyBadge difficulty={problem.difficulty} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-2">
        <ProblemStatementPanel problem={problem} />

        <div className="flex flex-col gap-4">
          <div className="min-h-[500px] lg:min-h-[600px] flex-1">
            <CodeWorkspace
              language={language}
              onLanguageChange={changeLanguage}
              availableLanguages={availableLanguages}
              code={code}
              onCodeChange={setCode}
              onRun={handleRun}
              onSubmit={handleSubmit}
              onReset={resetCode}
              isRunning={isRunning}
              isSubmitting={isSubmitting}
            />
          </div>

          <section>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Console
            </h3>

            <ConsolePanel
              runResult={runResult}
              runError={runError}
              isRunning={isRunning}
            />
          </section>

          <section>
            <div className="flex items-center justify-between gap-4 rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
              <span>
                Problem {neighborState.position} of {neighborState.total}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleNavigateProblem(neighborState.previousProblemId)}
                  disabled={!neighborState.previousProblemId}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-300 transition hover:border-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => handleNavigateProblem(neighborState.nextProblemId)}
                  disabled={!neighborState.nextProblemId}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-300 transition hover:border-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>

            <SubmissionResultPanel
              submitResult={submitResult}
              submitError={submitError}
              onNextProblem={() => {
                if (neighborState.nextProblemId) {
                  handleNavigateProblem(neighborState.nextProblemId)
                } else {
                  navigate('/coding')
                }
              }}
            />
          </section>
        </div>
      </div>
    </div>
  )
}

export default CodingProblemPage