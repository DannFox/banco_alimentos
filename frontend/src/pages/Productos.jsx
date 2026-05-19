import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth/AuthContext'

export default function Productos() {
  const { puedeEditarProductos } = useAuth()
  const [items, setItems] = useState([])
  const [form, setForm] = useState({
    nombre: '',
    codigo_barras: '',
    cantidad: 0,
    fecha_vencimiento: '',
  })
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const load = async () => {
    const { data } = await api.get('/api/productos/')
    setItems(data)
  }

  useEffect(() => {
    load().catch(() => setErr('Sin permiso o error de red.'))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    setMsg('')
    try {
      await api.post('/api/productos/', {
        ...form,
        cantidad: Number(form.cantidad),
      })
      setMsg('Producto creado.')
      setForm({ nombre: '', codigo_barras: '', cantidad: 0, fecha_vencimiento: '' })
      await load()
    } catch (ex) {
      setErr(JSON.stringify(ex.response?.data || 'Error'))
    }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar producto?')) return
    await api.delete(`/api/productos/${id}/`)
    await load()
  }

  return (
    <>
      <h1 style={{ color: '#1b4332' }}>Productos</h1>
      <p>Crea un producto para almacenarlo.</p>

      {puedeEditarProductos && (
        <div className="card">
          <h2>Nuevo producto</h2>
          <form onSubmit={submit}>
            <div className="field">
              <label>Nombre</label>
              <input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="field">
              <label>Código de barras (opcional)</label>
              <input value={form.codigo_barras} onChange={(e) => setForm({ ...form, codigo_barras: e.target.value })} />
            </div>
            <div className="field">
              <label>Cantidad inicial</label>
              <input
                type="number"
                min={0}
                value={form.cantidad}
                onChange={(e) => setForm({ ...form, cantidad: e.target.value })}
              />
            </div>
            <div className="field">
              <label>Fecha de vencimiento</label>
              <input
                type="date"
                value={form.fecha_vencimiento}
                onChange={(e) => setForm({ ...form, fecha_vencimiento: e.target.value })}
                required
              />
            </div>
            {msg && <p className="success">{msg}</p>}
            {err && <p className="error">{err}</p>}
            <button type="submit" className="btn btn-primary">
              Guardar
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Listado</h2>
        <table className="data">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Código</th>
              <th>Cant.</th>
              <th>Vence</th>
              <th>Alerta</th>
              {puedeEditarProductos && <th></th>}
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td>{p.nombre}</td>
                <td>{p.codigo_barras || '—'}</td>
                <td>{p.cantidad}</td>
                <td>{p.fecha_vencimiento}</td>
                <td>{p.alerta_caducidad ? <span className="pill-warn">Sí</span> : 'No'}</td>
                {puedeEditarProductos && (
                  <td>
                    <button type="button" className="btn btn-danger-soft" onClick={() => eliminar(p.id)}>
                      Borrar
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
