import axios from 'axios'

const DEFAULT_BACKEND = 'http://127.0.0.1:8000'
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'
const STORAGE_KEY_ACCESS = 'placement_prep_access_token'
const STORAGE_KEY_REFRESH = 'placement_prep_refresh_token'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const readStoredToken = () => {
  if (typeof window !== 'undefined') {
    const storedToken = window.localStorage.getItem(STORAGE_KEY_ACCESS)
    if (storedToken) {
      return storedToken
    }
  }

  const defaultAuthorization = api.defaults.headers.common.Authorization
  if (typeof defaultAuthorization === 'string' && defaultAuthorization.startsWith('Bearer ')) {
    return defaultAuthorization.slice('Bearer '.length)
  }

  return null
}

const applyAuthorizationHeader = (headers, token) => {
  const targetHeaders = headers || {}

  if (token) {
    if (typeof targetHeaders.set === 'function') {
      targetHeaders.set('Authorization', `Bearer ${token}`)
    } else {
      targetHeaders.Authorization = `Bearer ${token}`
    }
  } else if (typeof targetHeaders.delete === 'function') {
    targetHeaders.delete('Authorization')
  } else {
    delete targetHeaders.Authorization
  }

  return targetHeaders
}

api.interceptors.request.use((config) => {
  const token = readStoredToken()
  config.headers = applyAuthorizationHeader(config.headers, token)
  return config
})

export const setAuthToken = (token) => {
  const bearerToken = token ? `Bearer ${token}` : null

  if (bearerToken) {
    api.defaults.headers.common.Authorization = bearerToken
    api.defaults.headers.Authorization = bearerToken
  } else {
    delete api.defaults.headers.common.Authorization
    delete api.defaults.headers.Authorization
  }

  if (typeof window !== 'undefined') {
    if (token) {
      window.localStorage.setItem(STORAGE_KEY_ACCESS, token)
    } else {
      window.localStorage.removeItem(STORAGE_KEY_ACCESS)
    }
  }
}

// Response interceptor to attempt refresh on 401 when a refresh token exists
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (!originalRequest || originalRequest._retry) return Promise.reject(error)

    if (error.response && error.response.status === 401) {
      const refreshToken = typeof window !== 'undefined' ? window.localStorage.getItem(STORAGE_KEY_REFRESH) : null
      if (!refreshToken) return Promise.reject(error)

      try {
        originalRequest._retry = true
        const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
        const newAccess = response.data?.data?.access_token ?? response.data?.access_token ?? response.data?.tokens?.access_token
        if (!newAccess) throw new Error('No access token in refresh response')

        setAuthToken(newAccess)
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(STORAGE_KEY_ACCESS, newAccess)
        }

        originalRequest.headers = applyAuthorizationHeader(originalRequest.headers, newAccess)
        return api(originalRequest)
      } catch (e) {
        if (typeof window !== 'undefined') {
          window.localStorage.removeItem(STORAGE_KEY_ACCESS)
          window.localStorage.removeItem(STORAGE_KEY_REFRESH)
        }
        setAuthToken(null)
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  },
)

export default api
