import { useEffect, useState } from 'react'
import api from '../services/api'
import { applyTheme, getStoredThemePreference, mapThemeForApi, setStoredThemePreference } from '../theme'

export default function SettingsPage() {
  const [theme, setTheme] = useState('default')
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const initialTheme = getStoredThemePreference()
    setTheme(initialTheme)
    applyTheme(initialTheme)

    const loadSettings = async () => {
      try {
        const response = await api.get('/settings')
        const data = response.data?.data ?? response.data
        const resolvedTheme = data?.theme || 'default'
        setTheme(resolvedTheme)
        setStoredThemePreference(resolvedTheme)
        applyTheme(resolvedTheme)
      } catch (err) {
        setError(err?.response?.data?.message || 'Unable to load settings')
      } finally {
        setLoading(false)
      }
    }

    loadSettings()
  }, [])

  const handlePasswordSave = async (event) => {
    event.preventDefault()
    setError('')
    setMessage('')
    try {
      const response = await api.put('/settings/password', passwords)
      setMessage(response.data?.message || 'Password updated')
      setPasswords({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      setError(err?.response?.data?.message || 'Unable to update password')
    }
  }

  const handleThemeSave = async (event) => {
    event.preventDefault()
    setError('')
    setMessage('')
    const nextTheme = theme
    const persistedTheme = setStoredThemePreference(nextTheme)
    applyTheme(persistedTheme)
    try {
      const response = await api.put('/settings/theme', { theme: mapThemeForApi(nextTheme) })
      setMessage(response.data?.message || 'Theme updated')
    } catch (err) {
      setError(err?.response?.data?.message || 'Unable to update theme')
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-2 py-3 sm:px-4 sm:py-4 lg:px-0">
      {message && (
        <div className="mb-3 rounded-xl border border-emerald-800/40 bg-emerald-950/30 px-3 py-2.5 text-sm text-emerald-300">
          {message}
        </div>
      )}

      {error && (
        <div className="mb-3 rounded-xl border border-rose-800/40 bg-rose-950/30 px-3 py-2.5 text-sm text-rose-300">
          {error}
        </div>
      )}

      <section className="rounded-2xl border border-slate-800/80 bg-slate-950/70 p-4 sm:p-5">
        <div className="mb-4">
          <h2 className="text-base font-semibold text-white">Security</h2>
        </div>

        <form onSubmit={handlePasswordSave} className="mx-auto flex w-full max-w-[28rem] flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Current Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              value={passwords.current_password}
              onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })}
              className="w-full rounded-xl border border-slate-700/70 bg-slate-900/70 px-3.5 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-slate-500 focus:outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">New Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              value={passwords.new_password}
              onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
              className="w-full rounded-xl border border-slate-700/70 bg-slate-900/70 px-3.5 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-slate-500 focus:outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Confirm New Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              value={passwords.confirm_password}
              onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })}
              className="w-full rounded-xl border border-slate-700/70 bg-slate-900/70 px-3.5 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-slate-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-between gap-3 pt-1">
            <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-400">
              <input
                type="checkbox"
                checked={showPassword}
                onChange={() => setShowPassword((value) => !value)}
                className="h-4 w-4 rounded border-slate-600 bg-slate-900 accent-accent"
              />
              Show password
            </label>
            <button type="submit" className="rounded-xl bg-accent px-3.5 py-2 text-sm font-semibold text-slate-950">
              {loading ? 'Loading...' : 'Save Password'}
            </button>
          </div>
        </form>
      </section>

      <section className="mt-3 rounded-2xl border border-slate-800/80 bg-slate-950/70 p-4 sm:p-5">
        <div className="mb-4">
          <h2 className="text-base font-semibold text-white">Appearance</h2>
        </div>

        <form onSubmit={handleThemeSave} className="mx-auto flex w-full max-w-[24rem] flex-col gap-3">
          <div className="flex items-center gap-2">
            {['light', 'default'].map((option) => (
              <label
                key={option}
                className={`flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-sm ${theme === option ? 'border-accent bg-slate-900/80 text-white' : 'border-slate-700/70 bg-slate-900/60 text-slate-300'}`}
              >
                <input
                  type="radio"
                  name="theme"
                  checked={theme === option}
                  onChange={() => setTheme(option)}
                  className="accent-accent"
                />
                <span className="capitalize">{option === 'default' ? 'Default' : 'Light'}</span>
              </label>
            ))}
          </div>

          <div className="flex justify-end">
            <button type="submit" className="rounded-xl bg-accent px-3.5 py-2 text-sm font-semibold text-slate-950">
              Save Theme
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
