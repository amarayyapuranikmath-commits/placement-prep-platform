const THEME_STORAGE_KEY = 'placement_prep_theme_preference'
const DEFAULT_THEME = 'default'

export function normalizeTheme(themeValue) {
  const normalized = (themeValue || '').toString().trim().toLowerCase()
  return normalized === 'light' ? 'light' : DEFAULT_THEME
}

export function mapThemeForApi(themeValue) {
  return normalizeTheme(themeValue) === 'light' ? 'light' : 'default'
}

export function getStoredThemePreference() {
  if (typeof window === 'undefined') {
    return DEFAULT_THEME
  }

  return normalizeTheme(window.localStorage.getItem(THEME_STORAGE_KEY) || DEFAULT_THEME)
}

export function setStoredThemePreference(themeValue) {
  const normalized = normalizeTheme(themeValue)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(THEME_STORAGE_KEY, normalized)
  }
  return normalized
}

export function applyTheme(themeValue) {
  const normalized = normalizeTheme(themeValue)

  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('theme-light', normalized === 'light')
    document.documentElement.style.colorScheme = normalized === 'light' ? 'light' : 'dark'
  }

  return normalized
}

export { DEFAULT_THEME, THEME_STORAGE_KEY }
