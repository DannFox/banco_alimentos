import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Movimientos() {
  const [movs, setMovs] = useState([])
  const [productos, setProductos] = useState([])
  const [codigo, setCodigo] = useState('')
  const [busqueda, setBusqueda] = useState(null)
  const [form, setForm] = useState({
    producto: '',
    tipo: 'entrada',
    cantidad: 1,
    nota: '',
  })
  const [err, setErr] = useState('')

  const load = async () => {
    const [m, p] = await Promise.all([api.get('/api/movimientos/'), api.get('/api/productos/')])
    setMovs(m.data)
    setProductos(p.data)
  }

  useEffect(() => {
    load().catch(() => setErr('Error al cargar movimientos.'))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      await api.post('/api/movimientos/', {
        producto: Number(form.producto),
        tipo: form.tipo,
        cantidad: Number(form.cantidad),
        nota: form.nota,
      })
      setForm({ ...form, cantidad: 1, nota: '' })
      await load()
    } catch (ex) {
      setErr(JSON.stringify(ex.response?.data || 'Error'))
    }
  }

  const buscar = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      const { data } = await api.post('/api/buscar-codigo/', { codigo_barras: codigo })
      setBusqueda(data.producto)
      setForm((f) => ({ ...f, producto: String(data.producto.id) }))
    } catch {
      setBusqueda(null)
      setErr('Código no encontrado.')
    }
  }

  return (
    <>
      <h1 style={{ color: '#1b4332' }}>Movimientos</h1>
      <p>Entradas y salidas en tiempo real (actualizan cantidad del producto).</p>

      <div className="card">
        <h2>Buscar por código de barras</h2>
        <form onSubmit={buscar} className="row-actions" style={{ alignItems: 'flex-end' }}>
          <div className="field" style={{ flex: 1, marginBottom: 0 }}>
            <label>Código</label>
            <input value={codigo} onChange={(e) => setCodigo(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-secondary">
            Buscar
          </button>
        </form>
        {busqueda && (
          <p className="success">
            Encontrado: {busqueda.nombre} (stock {busqueda.cantidad})
          </p>
        )}
      </div>

      <div className="card">
        <h2>Registrar movimiento</h2>
        <form onSubmit={submit}>
          <div className="field">
            <label>Producto</label>
            <select value={form.producto} onChange={(e) => setForm({ ...form, producto: e.target.value })} required>
              <option value="">— Elegir —</option>
              {productos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre} ({p.cantidad})
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Tipo</label>
            <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
              <option value="entrada">Entrada</option>
              <option value="salida">Salida</option>
            </select>
          </div>
          <div className="field">
            <label>Cantidad</label>
            <input
              type="number"
              min={1}
              value={form.cantidad}
              onChange={(e) => setForm({ ...form, cantidad: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Nota</label>
            <input value={form.nota} onChange={(e) => setForm({ ...form, nota: e.target.value })} />
          </div>
          {err && <p className="error">{err}</p>}
          <button type="submit" className="btn btn-primary">
            Registrar
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Historial reciente</h2>
        <table className="data">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Producto</th>
              <th>Tipo</th>
              <th>Cant.</th>
              <th>Usuario</th>
            </tr>
          </thead>
          <tbody>
            {movs.slice(0, 40).map((m) => (
              <tr key={m.id}>
                <td>{new Date(m.registrado_en).toLocaleString()}</td>
                <td>{m.producto_nombre}</td>
                <td>{m.tipo}</td>
                <td>{m.cantidad}</td>
                <td>{m.usuario_username}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
