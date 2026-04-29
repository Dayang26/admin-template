import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

const STORAGE_KEY = 'ui-theme'

function getSystemTheme(): 'light' | 'dark' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Theme | null
    return stored ?? 'system'
  })

  useEffect(() => {
    const root = document.documentElement
    const resolved = theme === 'system' ? getSystemTheme() : theme

    root.classList.remove('light', 'dark')
    root.classList.add(resolved)
  }, [theme])

  useEffect(() => {
    if (theme !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      // 只有在没有强制系统默认主题时，才直接用 OS 主题
      const systemDefault = window.localStorage.getItem('system-theme-fallback') || 'system'
      const root = document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(systemDefault === 'system' ? getSystemTheme() : (systemDefault as 'light' | 'dark'))
    }

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [theme])

  // 监听来自系统配置的默认主题
  useEffect(() => {
    const handleSystemThemeChange = (e: CustomEvent) => {
      const defaultTheme = e.detail
      window.localStorage.setItem('system-theme-fallback', defaultTheme)
      
      const stored = localStorage.getItem(STORAGE_KEY) as Theme | null
      if (!stored || stored === 'system') {
        const root = document.documentElement
        const resolved = defaultTheme === 'system' ? getSystemTheme() : defaultTheme
        root.classList.remove('light', 'dark')
        root.classList.add(resolved)
      }
    }
    window.addEventListener('system-theme-default', handleSystemThemeChange as EventListener)
    return () => window.removeEventListener('system-theme-default', handleSystemThemeChange as EventListener)
  }, [])

  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(STORAGE_KEY, newTheme)
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme 必须在 ThemeProvider 内部使用')
  }
  return context
}
