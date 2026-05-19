import { useEffect, useState } from 'react'
import { api } from '../api'
import './EstructurasDatos.css'

function claseUrgencia(urg) {
  switch (urg) {
    case 'VENCIDO':
      return 'ed-urg--vencido'
    case 'CRÍTICO':
      return 'ed-urg--critico'
    case 'URGENTE':
    case 'PRÓXIMO':
      return 'ed-urg--urgente'
    default:
      return 'ed-urg--muted'
  }
}

export default function EstructurasDatos() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancel = false
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const { data: payload } = await api.get('/api/publico/estructuras/')
        if (!cancel) setData(payload)
      } catch {
        if (!cancel) {
          setError(
            'No se pudo cargar el inventario. Comprueba que el backend esté en marcha (puerto 8000) y la base de datos activa.',
          )
        }
      } finally {
        if (!cancel) setLoading(false)
      }
    }
    load()
    return () => {
      cancel = true
    }
  }, [])

  const cola = data?.cola_prioridad
  const th = data?.tabla_hash
  const raiz = cola?.raiz
  const top = cola?.top ?? []
  const totalHeap = cola?.total_en_heap ?? 0

  const pctBarra = th ? Math.min(100, th.factor_carga_pct) : 0

  return (
    <div className="estructuras-root">
      <header className="estructuras-hero">
        <h1>ESTRUCTURAS DE DATOS</h1>
        <p>
          Detalles técnicos de la <strong>cola de prioridad</strong> y la <strong>tabla hash</strong> con{' '}
          <strong>datos reales</strong> del inventario del banco (solo lectura, sin iniciar sesión).
        </p>
        {data?.actualizado_en && (
          <p style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
            Actualizado: {new Date(data.actualizado_en).toLocaleString()}
          </p>
        )}
      </header>

      {loading && (
        <div className="ed-card">
          <p className="ed-prose">Cargando datos del servidor…</p>
        </div>
      )}
      {error && (
        <div className="ed-card" style={{ borderColor: '#e63946' }}>
          <p className="ed-prose" style={{ color: '#ff6b6b' }}>
            {error}
          </p>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <section className="ed-card" aria-labelledby="cola-titulo">
            <div className="ed-card__head">
              <h2 id="cola-titulo" className="ed-card__title">
                COLA DE PRIORIDAD
              </h2>
              <span className="ed-badge ed-badge--active">{totalHeap > 0 ? 'ACTIVA' : 'VACÍA'}</span>
            </div>
            <p className="ed-card__subtitle">
              Min-Heap — productos <strong>con stock</strong> ordenados por fecha de vencimiento (misma lógica que el
              panel interno).
            </p>

            <div className="ed-metrics" role="group" aria-label="Métricas reales de la cola">
              <div className="ed-metric">
                <strong>{totalHeap}</strong>
                <span>Productos en el heap</span>
              </div>
              <div className="ed-metric">
                <strong>O(1)</strong>
                <span>Ver mínimo (raíz)</span>
              </div>
              <div className="ed-metric">
                <strong>O(log N)</strong>
                <span>Insertar / extraer</span>
              </div>
            </div>

            <h3 className="ed-card__title" style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              ¿Cómo funciona?
            </h3>
            <p className="ed-prose">
              Un <strong>min-heap</strong> mantiene el vencimiento más próximo en la raíz. El backend construye la cola
              con <code style={{ color: '#ff8c42' }}>heapq</code> sobre los productos con cantidad &gt; 0; lo que ves
              abajo es ese orden aplicado a tu base de datos actual.
            </p>

            <div className="ed-root" role="region" aria-label="Producto más urgente según inventario real">
              <h3>Raíz del heap (producto más urgente)</h3>
              {raiz ? (
                <>
                  <div className="nombre">{raiz.nombre}</div>
                  <div className="meta">
                    Vence: {raiz.fecha_vencimiento} — {raiz.dias_para_vencer} días respecto a hoy — {raiz.cantidad}{' '}
                    u. en stock
                  </div>
                  <div style={{ marginTop: '0.65rem' }}>
                    <span className={`ed-urg ${claseUrgencia(raiz.urgencia)}`}>{raiz.urgencia}</span>
                  </div>
                </>
              ) : (
                <p className="ed-prose" style={{ margin: 0 }}>
                  No hay productos con stock para mostrar en la cola. Cuando registres existencias, aparecerán aquí en
                  vivo.
                </p>
              )}
            </div>

            <h3 className="ed-card__title" style={{ fontSize: '0.85rem', margin: '1rem 0 0.5rem' }}>
              Top 5 urgentes (orden real del heap)
            </h3>
            {top.length === 0 ? (
              <p className="ed-prose">Sin entradas.</p>
            ) : (
              <ol className="ed-list">
                {top.map((p, i) => (
                  <li key={p.id}>
                    <span>
                      <strong style={{ color: '#ff8c42', marginRight: '0.35rem' }}>{i + 1}.</strong>
                      {p.nombre}
                      <span style={{ color: 'var(--ed-muted)', marginLeft: '0.5rem' }}>| {p.fecha_vencimiento}</span>
                    </span>
                    <span className={`ed-urg ${claseUrgencia(p.urgencia)}`}>{p.urgencia}</span>
                  </li>
                ))}
              </ol>
            )}
          </section>

          <section className="ed-card" aria-labelledby="hash-titulo">
            <div className="ed-card__head">
              <h2 id="hash-titulo" className="ed-card__title">
                TABLA HASH
              </h2>
              <span className="ed-badge ed-badge--active">{th?.total_elementos > 0 ? 'ACTIVA' : 'VACÍA'}</span>
            </div>
            <p className="ed-card__subtitle">
              Simulación de cubetas con encadenamiento a partir del <strong>mismo catálogo</strong> que alimenta el
              índice <code>dict</code> (claves <code>id_*</code> y <code>bc_*</code>) en las búsquedas por código.
            </p>

            <div className="ed-metrics" role="group" aria-label="Métricas derivadas del catálogo real">
              <div className="ed-metric">
                <strong>{th?.total_elementos ?? 0}</strong>
                <span>Claves en el índice</span>
              </div>
              <div className="ed-metric">
                <strong>{th?.capacidad_cubetas ?? 64}</strong>
                <span>Capacidad (cubetas)</span>
              </div>
              <div className="ed-metric">
                <strong>{th?.factor_carga_pct ?? 0}%</strong>
                <span>Factor de carga</span>
              </div>
            </div>

            <div className="ed-bar-wrap">
              <div
                className="ed-bar"
                role="progressbar"
                aria-valuenow={Math.round(pctBarra)}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <span style={{ width: `${pctBarra}%` }} />
              </div>
              <div className="ed-bar-labels">
                <span>
                  Catálogo: {th?.productos_catalogo ?? 0} productos · {th?.claves_id ?? 0} claves ID ·{' '}
                  {th?.claves_codigo_barras ?? 0} códigos de barras
                </span>
                <span>Límite típico redimensión: 75%</span>
              </div>
            </div>

            <p className="ed-prose" style={{ fontSize: '0.85rem' }}>
              Cubetas ocupadas: <strong>{th?.cubetas_ocupadas ?? 0}</strong> · Inserciones con colisión:{' '}
              <strong>{th?.inserciones_con_colision ?? 0}</strong> · Cadena máxima en una cubeta:{' '}
              <strong>{th?.max_cadena ?? 0}</strong>
            </p>

            <h3 className="ed-card__title" style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              ¿Cómo funciona?
            </h3>
            <p className="ed-prose">
              Cada producto aporta al menos una clave numérica (ID); si tiene código de barras, otra clave derivada con
              hash tipo <strong>Horner</strong> sobre la cadena. Se reparten en <strong>m</strong> cubetas; si la
              densidad supera <strong>75%</strong>, en una tabla dinámica se duplicaría <strong>m</strong> (aquí se
              calcula la <strong>m</strong> mínima que mantiene la carga ≤ 75% con tus datos actuales).
            </p>

            <h3 className="ed-card__title" style={{ fontSize: '0.85rem', margin: '1rem 0 0.65rem' }}>
              Pseudocódigo simplificado
            </h3>
            <div className="ed-pseudo-grid">
              <div className="ed-pseudo">
                <h4>Cola de prioridad — insertar</h4>
                <pre>{`FUNCIÓN insertar(heap, producto):
    agregar producto al final del heap
    i ← índice del nuevo nodo
    MIENTRAS i > 0 Y fecha(i) < fecha(padre(i)):
        intercambiar(i, padre(i))
        i ← padre(i)`}</pre>
              </div>
              <div className="ed-pseudo">
                <h4>Tabla hash — buscar por ID</h4>
                <pre>{`FUNCIÓN buscar(tabla, id):
    índice ← HASH(id) % capacidad
    nodo ← tabla[índice]
    MIENTRAS nodo ≠ NULO:
        SI nodo.clave = id:
            RETORNAR nodo.valor
        nodo ← nodo.siguiente
    RETORNAR NULO`}</pre>
              </div>
            </div>

            <p className="ed-note">
              Los valores se calculan al momento de la petición sobre tu base MySQL configurada. Esta ruta es pública
              solo para lectura; modificar inventario sigue requiendo usuario y contraseña en el resto del sistema.
            </p>
          </section>

          <div className="ed-legend" aria-hidden="true">
            <span>
              <span className="ed-dot ed-dot--green" /> Cola de prioridad (heap)
            </span>
            <span>
              <span className="ed-dot ed-dot--orange" /> Tabla hash (estadísticas en vivo)
            </span>
          </div>
        </>
      )}
    </div>
  )
}
