import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { setAuthToken } from '../services/api'
import { login as loginRequest, register as registerRequest, fetchCurrentUser } from '../services/authService'
import { applyTheme, setStoredThemePreference } from '../theme'

export const AuthContext = createContext(null)

const STORAGE_KEY_ACCESS = 'placement_prep_access_token'
const STORAGE_KEY_REFRESH = 'placement_prep_refresh_token'
const STORAGE_KEY_USER = 'placement_prep_user'

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_USER)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  })
  const [isLoading, setIsLoading] = useState(true)
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem(STORAGE_KEY_ACCESS))

  const loadCurrentUser = useCallback(async (token = accessToken) => {
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      setAuthToken(token)
      const response = await fetchCurrentUser()
      const userObj = response.data ?? response
      setUser(userObj)
      try {
        localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(userObj))
      } catch {}

      try {
        const settingsResponse = await api.get('/settings')
        const settingsData = settingsResponse.data?.data ?? settingsResponse.data
        const resolvedTheme = settingsData?.theme || 'default'
        setStoredThemePreference(resolvedTheme)
        applyTheme(resolvedTheme)
      } catch {
        applyTheme('default')
      }
    } catch (error) {
      setAccessToken(null)
      localStorage.removeItem(STORAGE_KEY_ACCESS)
      localStorage.removeItem(STORAGE_KEY_REFRESH)
      localStorage.removeItem(STORAGE_KEY_USER)
      setUser(null)
      setAuthToken(null)
    } finally {
      setIsLoading(false)
    }
  }, [accessToken])

  useEffect(() => {
    loadCurrentUser(accessToken)
  }, [accessToken, loadCurrentUser])

  const login = async ({ email, password }) => {
    const response = await loginRequest({ email, password })
    const payload = response?.data ?? response
    const token = payload?.tokens?.access_token || payload?.access_token || payload?.data?.tokens?.access_token || payload?.data?.access_token
    const refresh = payload?.tokens?.refresh_token || payload?.refresh_token || payload?.data?.tokens?.refresh_token || payload?.data?.refresh_token

    if (!token) {
      throw new Error('Unable to retrieve access token from login response.')
    }

    localStorage.setItem(STORAGE_KEY_ACCESS, token)
    if (refresh) localStorage.setItem(STORAGE_KEY_REFRESH, refresh)
    setAccessToken(token)
    setAuthToken(token)

    await loadCurrentUser(token)
    navigate('/dashboard')
  }

  const register = async (payload) => {
    const response = await registerRequest(payload)
    return response.data ?? response
  }

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY_ACCESS)
    localStorage.removeItem(STORAGE_KEY_REFRESH)
    localStorage.removeItem(STORAGE_KEY_USER)
    setAccessToken(null)
    setUser(null)
    setAuthToken(null)
    navigate('/login')
  }

  const value = useMemo(
    () => ({ user, isLoading, login, register, logout, isAuthenticated: Boolean(user) }),
    [user, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
