import { useEffect, useState } from 'react'
import { api } from '../api'

const ROLES = [
  { value: 'administrador', label: 'Administrador' },
  { value: 'coordinador', label: 'Coordinador' },
  { value: 'voluntario', label: 'Voluntario' },
]

export default function AdminUsuarios() {
  const [users, setUsers] = useState([])
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')

  const load = async () => {
    const { data } = await api.get('/api/auth/usuarios/')
    setUsers(data)
  }

  useEffect(() => {
    load().catch(() => setErr('Solo administradores ven esta lista.'))
  }, [])

  const cambiar = async (username, rol) => {
    setErr('')
    setMsg('')
    try {
      await api.post('/api/auth/cambiar-rol/', { username, rol })
      setMsg(`Rol actualizado: ${username}`)
      await load()
    } catch (e) {
      setErr('No se pudo cambiar el rol.')
    }
  }

  return (
    <>
      <h1 style={{ color: '#1b4332' }}>Usuarios y roles</h1>
      {err && <p className="error">{err}</p>}
      {msg && <p className="success">{msg}</p>}
      <div className="card">
        <table className="data">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nombre</th>
              <th>Rol actual</th>
              <th>Cambiar a</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.perfil?.nombre_completo}</td>
                <td>{u.perfil?.rol_display || u.perfil?.rol}</td>
                <td>
                  <div className="row-actions">
                    {ROLES.map((r) => (
                      <button
                        key={r.value}
                        type="button"
                        className="btn btn-secondary"
                        disabled={u.perfil?.rol === r.value}
                        onClick={() => cambiar(u.username, r.value)}
                      >
                        {r.label}
                      </button>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
