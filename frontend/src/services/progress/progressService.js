import api from '../../services/api'

let _cachedSummary = null
let _cachedAt = 0
const CACHE_TTL_MS = 60 * 1000 // 1 minute cache

const _fetchSummary = async (force = false) => {
  const now = Date.now()
  if (!force && _cachedSummary && now - _cachedAt < CACHE_TTL_MS) {
    return _cachedSummary
  }

  const response = await api.get('/progress')
  const payload = response.data?.data ?? response.data ?? {}
  _cachedSummary = payload
  _cachedAt = Date.now()
  return payload
}

export const getProgressOverview = async (opts = { force: false }) => {
  try {
    const summary = await _fetchSummary(opts.force)
    return { overall: summary.overview ?? null }
  } catch (err) {
    throw err
  }
}

export const getProgressModules = async (opts = { force: false }) => {
  try {
    const summary = await _fetchSummary(opts.force)
    return { modules: summary.modules ?? [] }
  } catch (err) {
    throw err
  }
}

export const getProgressAnalytics = async (moduleKey) => {
  try {
    const params = moduleKey ? { module: moduleKey } : {}
    const response = await api.get('/progress/analytics', { params })
    const points = response.data?.data?.points ?? []
    return { points }
  } catch (err) {
    throw err
  }
}

export const getRecentActivity = async (opts = { force: false }) => {
  try {
    const summary = await _fetchSummary(opts.force)
    return { activity: summary.activity ?? [] }
  } catch (err) {
    throw err
  }
}

export const getProgressModuleHistory = async (moduleKey) => {
  const normalizedModule = (moduleKey || 'interview').toLowerCase()

  if (normalizedModule === 'aptitude') {
    const response = await api.get('/aptitude/history')
    const payload = response.data?.data ?? response.data ?? {}
    return payload.history ?? []
  }

  if (normalizedModule === 'coding') {
    const response = await api.get('/coding/submissions')
    const payload = response.data?.data ?? response.data ?? {}
    return payload.submissions ?? []
  }

  if (normalizedModule === 'resume') {
    const response = await api.get('/resume/history')
    const payload = response.data?.data ?? response.data ?? {}
    return payload.resumes ?? []
  }

  const response = await api.get('/interview/history')
  const payload = response.data?.data ?? response.data ?? {}
  return payload.history ?? []
}

export const downloadProgressReport = async () => {
  const response = await api.get('/progress/report', { responseType: 'blob' })
  return response
}
