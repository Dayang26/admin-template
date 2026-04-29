import React, { createContext, useContext, useEffect } from 'react'
import { usePublicSystemSettings } from '../hooks/use-system-settings'
import type { SystemSettingPublic } from '../types/system-setting'

interface SystemSettingsContextType {
  settings: SystemSettingPublic | undefined
  isLoading: boolean
  error: Error | null
}

const SystemSettingsContext = createContext<SystemSettingsContextType | undefined>(
  undefined
)

export function SystemSettingsProvider({ children }: { children: React.ReactNode }) {
  const { data: settings, isLoading, error } = usePublicSystemSettings()

  // Apply Favicon and Theme Color when settings change
  useEffect(() => {
    if (!settings) return

    // Apply Favicon
    let link: HTMLLinkElement | null = document.querySelector("link[rel~='icon']")
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.head.appendChild(link)
    }

    if (settings.favicon_url) {
      link.href = settings.favicon_url
    } else {
      link.href = '/favicon.svg'
    }

    // Apply Theme Color
    if (settings.primary_color) {
      try {
        document.documentElement.style.setProperty('--primary', settings.primary_color)
      } catch (e) {
        console.error('Failed to parse primary color', e)
      }
    }

    // Apply Theme Mode globally
    if (settings.theme_mode) {
      window.dispatchEvent(new CustomEvent('system-theme-default', { detail: settings.theme_mode }))
    }
  }, [settings])

  return (
    <SystemSettingsContext.Provider value={{ settings, isLoading, error }}>
      {children}
    </SystemSettingsContext.Provider>
  )
}

export function useSystemSettingsContext() {
  const context = useContext(SystemSettingsContext)
  if (context === undefined) {
    throw new Error('useSystemSettingsContext must be used within a SystemSettingsProvider')
  }
  return context
}
