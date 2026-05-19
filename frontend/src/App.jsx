import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Layout from './components/Layout'
import AdminUsuarios from './pages/AdminUsuarios'
import Dashboard from './pages/Dashboard'
import EstructurasDatos from './pages/EstructurasDatos'
import Login from './pages/Login'
import Movimientos from './pages/Movimientos'
import Productos from './pages/Productos'
import Registro from './pages/Registro'
import './App.css'

function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="card">
        <p>Cargando sesión…</p>
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  return children
}

function RequireAdmin({ children }) {
  const { esAdmin, loading, user } = useAuth()
  if (loading) {
    return (
      <div className="card">
        <p>Cargando…</p>
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (!esAdmin) {
    return <Navigate to="/" replace />
  }
  return children
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/estructuras" element={<EstructurasDatos />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/productos"
          element={
            <RequireAuth>
              <Productos />
            </RequireAuth>
          }
        />
        <Route
          path="/movimientos"
          element={
            <RequireAuth>
              <Movimientos />
            </RequireAuth>
          }
        />
        <Route
          path="/admin/usuarios"
          element={
            <RequireAdmin>
              <AdminUsuarios />
            </RequireAdmin>
          }
        />
      </Route>
    </Routes>
  )
}
