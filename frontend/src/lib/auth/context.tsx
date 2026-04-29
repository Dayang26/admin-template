import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import type { UserDetail } from '../types/user'
import { apiClient } from '../api/client'

interface AuthContextType {
  user: UserDetail | null
  token: string | null
  isLoading: boolean
  login: (token: string) => Promise<UserDetail | undefined>
  logout: () => void
  hasPermission: (permission: string) => boolean
  isSuperuser: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserDetail | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(() => Boolean(localStorage.getItem('token')))
  const navigate = useNavigate()

  const fetchMe = useCallback(async () => {
    try {
      const data = await apiClient<UserDetail>('/api/v1/users/me')
      setUser(data)
      return data
    } catch (error) {
      console.error('获取用户信息失败', error)
      localStorage.removeItem('token')
      setUser(null)
      setToken(null)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = useCallback(
    async (newToken: string) => {
      localStorage.setItem('token', newToken)
      setToken(newToken)
      return await fetchMe()
    },
    [fetchMe],
  )

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
    setToken(null)
    navigate('/login')
  }, [navigate])

  useEffect(() => {
    if (token) {
      queueMicrotask(() => {
        void fetchMe()
      })
    }
  }, [fetchMe, token])

  const hasPermission = useCallback(
    (permission: string) => {
      if (!user) return false
      // superuser 拥有所有权限
      if (user.roles.includes('superuser')) return true
      return user.permissions?.includes(permission) ?? false
    },
    [user],
  )

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
    hasPermission,
    isSuperuser: user?.roles.includes('superuser') ?? false,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth 必须在 AuthProvider 内部使用')
  }
  return context
}
