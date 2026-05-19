import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Registro() {
  const { register } = useAuth()
  const nav = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    nombre_completo: '',
  })
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setOk('')
    try {
      await register(form)
      setOk('Cuenta creada. Tu rol inicial es Voluntario. Ya puedes iniciar sesión.')
      setTimeout(() => nav('/login'), 2000)
    } catch (err) {
      const msg = err.response?.data
      if (typeof msg === 'object') {
        setError(JSON.stringify(msg))
      } else {
        setError('No se pudo registrar.')
      }
    }
  }

  const ch = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div className="card auth-page">
      <h1>Registro</h1>
      <p className="success">Los nuevos usuarios entran como <strong>Voluntario</strong>. Un administrador puede cambiar tu rol.</p>
      <form onSubmit={submit}>
        <div className="field">
          <label>Nombre completo</label>
          <input value={form.nombre_completo} onChange={ch('nombre_completo')} />
        </div>
        <div className="field">
          <label>Usuario</label>
          <input value={form.username} onChange={ch('username')} required autoComplete="username" />
        </div>
        <div className="field">
          <label>Correo (opcional)</label>
          <input type="email" value={form.email} onChange={ch('email')} autoComplete="email" />
        </div>
        <div className="field">
          <label>Contraseña (mín. 8)</label>
          <input type="password" value={form.password} onChange={ch('password')} required minLength={8} />
        </div>
        {error && <p className="error">{error}</p>}
        {ok && <p className="success">{ok}</p>}
        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
          Crear cuenta
        </button>
      </form>
      <p style={{ marginTop: '1rem' }}>
        <Link to="/login">Volver al login</Link>
      </p>
    </div>
  )
}
