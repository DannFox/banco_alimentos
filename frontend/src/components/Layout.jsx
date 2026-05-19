import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { user, logout, rol, esAdmin } = useAuth()

  const linkStyle = ({ isActive }) => ({
    fontWeight: isActive ? 700 : 500,
    textDecoration: isActive ? 'underline' : 'none',
  })

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <strong style={{ marginRight: '1rem' }}>Banco de Alimentos</strong>
          <NavLink to="/estructuras" style={linkStyle}>
            Estructuras
          </NavLink>
          {user && (
            <>
              <NavLink to="/" style={linkStyle} end>
                Panel
              </NavLink>
              <NavLink to="/productos" style={linkStyle}>
                Productos
              </NavLink>
              <NavLink to="/movimientos" style={linkStyle}>
                Movimientos
              </NavLink>
              {esAdmin && (
                <NavLink to="/admin/usuarios" style={linkStyle}>
                  Usuarios
                </NavLink>
              )}
            </>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {user && (
            <>
              <span className="badge">{user.username}</span>
              <span className="badge">{rol}</span>
              <button type="button" className="btn btn-ghost" onClick={logout}>
                Salir
              </button>
            </>
          )}
          {!user && (
            <>
              <Link to="/login">Entrar</Link>
              <Link to="/registro">Registro</Link>
            </>
          )}
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  )
}
