import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { login, user, loading } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!loading && user) {
      nav('/')
    }
  }, [user, loading, nav])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      nav('/')
    } catch {
      setError('Usuario o contraseña incorrectos.')
    }
  }

  return (
    <div className="card auth-page">
      <h1>Iniciar sesión</h1>
      <form onSubmit={submit}>
        <div className="field">
          <label>Usuario</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username" />
        </div>
        <div className="field">
          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
          Entrar
        </button>
      </form>
      <p style={{ marginTop: '1rem' }}>
        ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
      </p>
    </div>
  )
}
