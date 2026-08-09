// src/services/resumeService.js
import api from './api'

const historyCache = { promise: null, lastLoadedAt: 0 }
const analysisCache = new Map()

const cacheGet = async (cacheKey, request) => {
  const existing = analysisCache.get(cacheKey)
  if (existing) {
    return existing
  }

  const pending = request()
  analysisCache.set(cacheKey, pending)

  try {
    const result = await pending
    return result
  } catch (error) {
    analysisCache.delete(cacheKey)
    throw error
  }
}

export const uploadResume = async (file, onUploadProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  // Deliberately unset Content-Type so the browser/axios sets the correct
  // multipart boundary itself. The shared `api` instance defaults to
  // application/json, which would break this request if left in place.
  const response = await api.post('/resume/upload', formData, {
    headers: { 'Content-Type': undefined },
    onUploadProgress,
  })
  const payload = response.data.data ?? response.data
  historyCache.promise = null
  analysisCache.clear()
  return payload
}

export const getResumeHistory = async () => {
  if (historyCache.promise) {
    const response = await historyCache.promise
    const data = response.data.data ?? response.data
    return data.resumes ?? []
  }

  historyCache.promise = api.get('/resume/history')

  try {
    const response = await historyCache.promise
    const data = response.data.data ?? response.data
    return data.resumes ?? []
  } catch (error) {
    historyCache.promise = null
    throw error
  }
}

export const getResumeAnalysis = async (resumeId) => {
  const cacheKey = String(resumeId)

  return cacheGet(cacheKey, async () => {
    const response = await api.get(`/resume/${resumeId}`)
    return response.data.data ?? response.data
  })
}

export const reanalyzeResume = async (resumeId) => {
  const response = await api.post(`/resume/${resumeId}/reanalyze`)
  const payload = response.data.data ?? response.data
  analysisCache.delete(String(resumeId))
  historyCache.promise = null
  return payload
}

export const deleteResume = async (resumeId) => {
  const response = await api.delete(`/resume/${resumeId}`)
  const payload = response.data.data ?? response.data
  analysisCache.delete(String(resumeId))
  historyCache.promise = null
  return payload
}