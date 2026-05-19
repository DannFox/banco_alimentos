import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = useCallback(async () => {
    const access = localStorage.getItem('access')
    if (!access) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get('/api/auth/yo/')
      setUser(data)
    } catch {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadMe()
  }, [loadMe])

  const login = async (username, password) => {
    const { data } = await api.post('/api/auth/login/', { username, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    await loadMe()
  }

  const register = async (payload) => {
    await api.post('/api/auth/registro/', payload)
  }

  const logout = () => {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    setUser(null)
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      reloadUser: loadMe,
      rol: user?.perfil?.rol,
      puedeExportar: ['administrador', 'coordinador'].includes(user?.perfil?.rol),
      puedeEditarProductos: ['administrador', 'coordinador'].includes(user?.perfil?.rol),
      esAdmin: user?.perfil?.rol === 'administrador',
    }),
    [user, loading, loadMe],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth fuera de AuthProvider')
  return ctx
}
