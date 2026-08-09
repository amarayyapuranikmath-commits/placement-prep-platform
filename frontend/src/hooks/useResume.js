import { useCallback, useEffect, useState } from 'react'
import {
  deleteResume,
  getResumeHistory,
  reanalyzeResume,
  uploadResume,
} from '../services/resumeService'

export const useResume = () => {
  const [history, setHistory] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const fetchHistory = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await getResumeHistory()
      setHistory(data)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load resume history')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  const upload = useCallback(
    async (file) => {
      setIsUploading(true)
      setUploadProgress(0)
      setError('')
      try {
        const analysis = await uploadResume(file, (event) => {
          if (event.total) {
            setUploadProgress(Math.round((event.loaded / event.total) * 100))
          }
        })
        await fetchHistory()
        return analysis
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to upload resume'
        setError(message)
        throw new Error(message)
      } finally {
        setIsUploading(false)
      }
    },
    [fetchHistory]
  )

  const reanalyze = useCallback(
    async (resumeId) => {
      const analysis = await reanalyzeResume(resumeId)
      await fetchHistory()
      return analysis
    },
    [fetchHistory]
  )

  const remove = useCallback(
    async (resumeId) => {
      await deleteResume(resumeId)
      await fetchHistory()
    },
    [fetchHistory]
  )

  const currentResume = history.find((item) => item.is_current) || null

  return {
    history,
    currentResume,
    isLoading,
    error,
    isUploading,
    uploadProgress,
    upload,
    reanalyze,
    remove,
    refetch: fetchHistory,
  }
}