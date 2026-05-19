import { useEffect, useState } from 'react'
import { api, downloadBlob } from '../api'
import { useAuth } from '../auth/AuthContext'

export default function Dashboard() {
  const { puedeExportar } = useAuth()
  const [resumen, setResumen] = useState(null)
  const [alertas, setAlertas] = useState([])
  const [cola, setCola] = useState([])
  const [err, setErr] = useState('')

  useEffect(() => {
    const run = async () => {
      try {
        const [d, a, c] = await Promise.all([
          api.get('/api/dashboard/'),
          api.get('/api/alertas/'),
          api.get('/api/cola-prioridad/'),
        ])
        setResumen(d.data)
        setAlertas(a.data)
        setCola(c.data.slice(0, 8))
      } catch (e) {
        setErr('No se pudo cargar el panel.')
      }
    }
    run()
  }, [])

  const expExcel = () => downloadBlob('/api/exportar/excel/', 'registro.xlsx')
  const expPdf = () => downloadBlob('/api/exportar/pdf/', 'registro.pdf')

  return (
    <>
      <h1 style={{ color: '#1b4332' }}>Panel del inventario</h1>
      <p>Cola de prioridad (FEFO) y alertas.</p>
      {err && <p className="error">{err}</p>}

      {resumen && (
        <div className="card grid-3">
          <div className="stat">
            <strong>{resumen.total_productos}</strong>
            <span>Productos registrados</span>
          </div>
          <div className="stat">
            <strong>{resumen.productos_con_stock}</strong>
            <span>Con stock</span>
          </div>
          <div className="stat">
            <strong>{resumen.alertas_proximas}</strong>
            <span>Alertas (≤7 días)</span>
          </div>
        </div>
      )}

      {puedeExportar && (
        <div className="card">
          <h2>Exportar registro del banco</h2>
          <p>Excel incluye inventario completo y movimientos. PDF: resumen e historial reciente.</p>
          <div className="row-actions">
            <button type="button" className="btn btn-secondary" onClick={expExcel}>
              Descargar Excel
            </button>
            <button type="button" className="btn btn-secondary" onClick={expPdf}>
              Descargar PDF
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Próximos a vencer (alertas)</h2>
        {alertas.length === 0 && <p>No hay alertas con stock.</p>}
        {alertas.length > 0 && (
          <ul className="alert-list">
            {alertas.map((p) => (
              <li key={p.id}>
                <span className="pill-warn">{p.fecha_vencimiento}</span> — {p.nombre} ({p.cantidad} u.)
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h2>Orden sugerido de salida (cola de prioridad)</h2>
        <ol>
          {cola.map((p) => (
            <li key={p.id}>
              {p.nombre} — vence {p.fecha_vencimiento} — {p.cantidad} u.
            </li>
          ))}
        </ol>
      </div>
    </>
  )
}
