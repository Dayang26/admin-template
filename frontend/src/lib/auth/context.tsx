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
  isStudent: boolean
  isTeacher: boolean
  isSuperuser: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserDetail | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
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
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      setToken(savedToken)
      fetchMe()
    } else {
      setIsLoading(false)
    }
  }, [fetchMe])

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
    isStudent: user?.roles.includes('student') ?? false,
    isTeacher: user?.roles.includes('teacher') ?? false,
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
