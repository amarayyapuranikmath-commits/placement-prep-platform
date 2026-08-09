import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { useCodingPreferences } from '../hooks/useCodingPreferences'
import { useProblemList } from '../hooks/useProblemList'
import { PROGRAMMING_LANGUAGES } from '../constants/languages'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import LanguagePickerModal from '../components/coding/LanguagePickerModal'
import ProblemFilters from '../components/coding/ProblemFilters'
import ProblemListTable from '../components/coding/ProblemListTable'

const CodingPage = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const {
    preferredLanguage,
    needsLanguageSelection,
    isLoading: isPrefLoading,
    isSaving,
    savePreferredLanguage,
    error: prefError,
  } = useCodingPreferences()

  const location = useLocation()
  const {
    problems,
    total,
    page,
    totalPages,
    search,
    category,
    difficulty,
    language,
    isLoading,
    error,
    setPage,
    setSearch,
    setCategory,
    setDifficulty,
    setLanguage,
  } = useProblemList(
    useMemo(() => ({
      search: searchParams.get('search') ?? '',
      category: searchParams.get('category') ?? '',
      difficulty: searchParams.get('difficulty') ?? '',
      language: searchParams.get('language') ?? '',
      page: Number(searchParams.get('page')) || 1,
    }), [searchParams]),
    location.state?.cachedList ?? null
  )

  const [languageFilter, setLanguageFilter] = useState(preferredLanguage ?? '')

  useEffect(() => {
    if (preferredLanguage) {
      setLanguageFilter(preferredLanguage)
      setLanguage(preferredLanguage)
    }
  }, [preferredLanguage, setLanguage])

  const handleLanguageChange = async (newLanguage) => {
    try {
      await savePreferredLanguage(newLanguage)
      setLanguageFilter(newLanguage)
      setLanguage(newLanguage)
    } catch {
      // save error is handled by useCodingPreferences
    }
  }

  useEffect(() => {
    const nextParams = new URLSearchParams()

    if (search) nextParams.set('search', search)
    if (category) nextParams.set('category', category)
    if (difficulty) nextParams.set('difficulty', difficulty)
    if (language) nextParams.set('language', language)
    if (page > 1) nextParams.set('page', String(page))

    setSearchParams(nextParams, { replace: true })
  }, [category, difficulty, language, page, search, setSearchParams])

  useEffect(() => {
    const savedScrollY = location.state?.filters?.scrollY
    if (typeof savedScrollY === 'number') {
      window.scrollTo(0, savedScrollY)
    }
  }, [location.state])

  if (isPrefLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6 lg:p-8">
      {needsLanguageSelection && (
        <LanguagePickerModal
          onSelect={handleLanguageChange}
          isSaving={isSaving}
          error={prefError}
        />
      )}

      <div className="space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-100">Coding Practice</h1>
            <p className="mt-1 text-sm text-slate-500">
              Sharpen your problem-solving skills with AI-generated coding challenges.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3 text-sm text-slate-300">
            Preferred language:&nbsp;
            <span className="font-medium text-slate-100">
              {languageFilter ? PROGRAMMING_LANGUAGES.find((item) => item.value === languageFilter)?.label : 'None'}
            </span>
          </div>
        </div>

        {prefError && <ErrorMessage message={prefError} />}
      </div>

      <ProblemFilters
        search={search}
        onSearchChange={setSearch}
        category={category}
        onCategoryChange={setCategory}
        difficulty={difficulty}
        onDifficultyChange={setDifficulty}
        language={language}
        onLanguageChange={handleLanguageChange}
      />

      {isLoading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner />
        </div>
      ) : error ? (
        <ErrorMessage message={error} />
      ) : (
        <ProblemListTable
          problems={problems}
          page={page}
          totalPages={totalPages}
          isLoading={isLoading}
          onPageChange={setPage}
          onSelectProblem={(id) => {
            const params = new URLSearchParams()
            if (search) params.set('search', search)
            if (category) params.set('category', category)
            if (difficulty) params.set('difficulty', difficulty)
            if (language) params.set('language', language)
            if (page > 1) params.set('page', String(page))
            const path = params.toString() ? `/coding/${id}?${params.toString()}` : `/coding/${id}`

            navigate(path, {
              state: {
                filters: { search, category, difficulty, language, page, scrollY: window.scrollY },
                cachedList: {
                  problems,
                  total,
                  page,
                  search,
                  category,
                  difficulty,
                  language,
                },
              },
            })
          }}
        />
      )}
    </div>
  )
}

export default CodingPage