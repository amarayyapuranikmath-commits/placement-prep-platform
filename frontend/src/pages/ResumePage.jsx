import { useEffect, useRef, useState } from 'react'
import { useResume } from '../hooks/useResume'
import { getResumeAnalysis } from '../services/resumeService'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import SuccessBanner from '../components/ui/SuccessBanner'
import ResumeUploadZone from '../components/resume/ResumeUploadZone'
import ResumePreviewCard from '../components/resume/ResumePreviewCard'
import ATSScoreGauge from '../components/resume/ATSScoreGauge'
import ScoreBreakdownGrid from '../components/resume/ScoreBreakdownGrid'
import AIAnalysisCards from '../components/resume/AIAnalysisCards'
import ResumeHistoryList from '../components/resume/ResumeHistoryList'
import ResumeActionBar from '../components/resume/ResumeActionBar'
import ResumeSectionScores from '../components/resume/ResumeSectionScores'
import ResumeKeywords from '../components/resume/ResumeKeywords'

const ResumePage = () => {
  const {
    history,
    currentResume,
    isLoading,
    error,
    isUploading,
    uploadProgress,
    upload,
    reanalyze,
    remove,
  } = useResume()

  const replaceInputRef = useRef(null)
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  const [isAnalysisLoading, setIsAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [isActionBusy, setIsActionBusy] = useState(false)

  const loadAnalysis = async (resumeId) => {
    if (!resumeId) {
      setSelectedAnalysis(null)
      return
    }
    setIsAnalysisLoading(true)
    setAnalysisError('')
    try {
      const analysis = await getResumeAnalysis(resumeId)
      setSelectedAnalysis(analysis)
    } catch (err) {
      setAnalysisError(err.response?.data?.message || 'Failed to load resume analysis')
    } finally {
      setIsAnalysisLoading(false)
    }
  }

  useEffect(() => {
    if (currentResume?.id) {
      loadAnalysis(currentResume.id)
    } else {
      setSelectedAnalysis(null)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentResume?.id])

  const handleFileSelected = async (file) => {
    try {
      const analysis = await upload(file)
      setSelectedAnalysis(analysis)
      setSuccessMessage('Resume uploaded and analyzed')
    } catch {
      // Failure is surfaced through the hook's `error` state below.
    }
  }

  const handleReplaceInputChange = (event) => {
    const file = event.target.files?.[0]
    if (file) handleFileSelected(file)
    event.target.value = ''
  }

  const handleReanalyze = async () => {
    if (!selectedAnalysis) return
    setIsActionBusy(true)
    try {
      const analysis = await reanalyze(selectedAnalysis.id)
      setSelectedAnalysis(analysis)
      setSuccessMessage('Resume re-analyzed')
    } catch {
      // Failure is surfaced through the hook's `error` state below.
    } finally {
      setIsActionBusy(false)
    }
  }

  const handleDelete = async () => {
    if (!selectedAnalysis) return
    setIsActionBusy(true)
    try {
      await remove(selectedAnalysis.id)
      setSelectedAnalysis(null)
      setSuccessMessage('Resume deleted')
    } catch {
      // Failure is surfaced through the hook's `error` state below.
    } finally {
      setIsActionBusy(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 px-4 sm:px-6 lg:px-8">
      <SuccessBanner message={successMessage} onDismiss={() => setSuccessMessage('')} />

      <div>
        <h1 className="text-xl font-semibold text-slate-100">Resume Analyzer</h1>
        <p className="mt-1 text-sm text-slate-500">
          AI analyzes your resume and provides ATS insights to help you land more interviews.
        </p>
      </div>

      {error && <ErrorMessage message={error} />}

      {!currentResume ? (
        <ResumeUploadZone
          onFileSelected={handleFileSelected}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
          hasExistingResume={false}
        />
      ) : (
        <div className="space-y-6">
          <ResumePreviewCard
            resume={currentResume}
            onReplaceClick={() => replaceInputRef.current?.click()}
          />

          {isUploading && (
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
              <p className="mb-2 text-sm text-slate-300">Uploading and analyzing...</p>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-accent transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {isAnalysisLoading && (
            <div className="flex justify-center py-10">
              <LoadingSpinner />
            </div>
          )}

          {analysisError && (
            <ErrorMessage
              message={analysisError}
              onRetry={() => loadAnalysis(currentResume.id)}
            />
          )}

          {selectedAnalysis && !isAnalysisLoading && (
            <>
              {/* FIRST ROW: ATS (3/12) + Insights (9/12) */}
              <div className="grid grid-cols-12 gap-6 items-stretch">
                <div className="col-span-12 lg:col-span-3">
                  <ATSScoreGauge
                    score={selectedAnalysis.ats_score || 0}
                    qualityLabel={selectedAnalysis.quality_label}
                  />
                </div>
                <div className="col-span-12 lg:col-span-9">
                  <ScoreBreakdownGrid
                    breakdown={selectedAnalysis.score_breakdown}
                    roleMatch={selectedAnalysis.role_match}
                    keywordMatch={selectedAnalysis.keyword_match}
                    sectionScores={selectedAnalysis.section_scores}
                    hideSectionScores={true}
                  />
                </div>
              </div>

              {/* SECOND ROW: Four equal cards (full-width grid displays 4 cards) */}
              <div className="col-span-12">
                <AIAnalysisCards
                  strengths={selectedAnalysis.strengths}
                  weaknesses={selectedAnalysis.weaknesses}
                  missingSkills={selectedAnalysis.missing_skills}
                  suggestions={selectedAnalysis.suggestions}
                  keywords={null}
                />
              </div>

              {/* THIRD ROW: Keywords (full width) */}
              <div>
                <ResumeKeywords keywords={selectedAnalysis.keywords} />
              </div>

              {/* FOURTH ROW: Section Scores */}
              <div>
                <ResumeSectionScores sectionScores={selectedAnalysis.section_scores} />
              </div>

              {/* BOTTOM: Action buttons (left aligned) */}
              <div className="mt-4">
                <ResumeActionBar
                  onReanalyze={handleReanalyze}
                  onReplace={() => replaceInputRef.current?.click()}
                  onDelete={handleDelete}
                  isBusy={isActionBusy}
                />
              </div>
            </>
          )}

          <ResumeHistoryList
            history={history}
            activeResumeId={currentResume?.id}
            onView={loadAnalysis}
          />
        </div>
      )}

      <input
        ref={replaceInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleReplaceInputChange}
      />
    </div>
  )
}

export default ResumePage