# Banco de Alimentos — Optimizador de Inventario

Sistema web para gestionar un inventario de alimentos con control de entradas/salidas, alertas de caducidad, exportación (Excel/PDF) y una vista pública que demuestra estructuras de datos (cola de prioridad y tabla hash) usando datos reales del inventario.

## Arquitectura

- **Backend**: Django + Django REST Framework + JWT (SimpleJWT) + MySQL
- **Frontend**: React + Vite (proxy a `/api` hacia el backend)

Carpetas principales:

- `backend/`: API, permisos por rol, modelos, exportación y comandos de gestión
- `frontend/`: UI (login, productos, movimientos, dashboard, admin usuarios, estructuras)

## Requisitos

- **Python** 3.10+ (recomendado 3.11/3.12)
- **Node.js** 18+ (recomendado 20+)
- **MySQL** 8+ (o compatible)

## Configuración (Backend)

### 1) Crear y activar entorno virtual

Desde `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3) Configurar MySQL

Por defecto el backend intenta conectarse a:

- Base: `banco_alimentos2`
- Usuario: `root`
- Host: `127.0.0.1`
- Puerto: `3306`

Puedes cambiarlo con variables de entorno (ver abajo). Crea la base en MySQL:

```sql
CREATE DATABASE banco_alimentos2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4) Variables de entorno (`backend/.env`)

El proyecto carga variables con `python-dotenv`. Crea un archivo `backend/.env` (opcional; hay defaults para desarrollo):

```env
DJANGO_SECRET_KEY=dev-only-change-in-production
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

MYSQL_DATABASE=banco_alimentos2
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

### 5) Migraciones

```powershell
python manage.py migrate
```

### 6) Crear usuario administrador (para acceder a la UI)

Crea un usuario (superusuario de Django):

```powershell
python manage.py createsuperuser
```

Luego asígnale rol **Administrador** (para permisos del sistema):

```powershell
python manage.py promover_admin TU_USUARIO
```

### 7) Cargar datos de ejemplo (alimentos + movimientos)

Esto crea productos con vencimientos variados, stock y movimientos de entrada/salida para que el sistema “se vea funcionando” (alertas, dashboard, cola de prioridad, búsqueda por código, etc.):

```powershell
python manage.py seed_demo_inventario --reseed
```

Opciones:

- `--reseed`: re-siembra los productos DEMO (borra movimientos de esos productos y recalcula stock)
- `--only-if-empty`: solo si la BD no tiene productos (modo seguro)

### 8) Levantar el servidor

```powershell
python manage.py runserver
```

Backend por defecto en `http://127.0.0.1:8000`.

## Configuración (Frontend)

Desde `frontend/`:

```powershell
npm install
npm run dev
```

Frontend por defecto en `http://localhost:5173`.

### Proxy a la API

Vite ya está configurado para proxyear `/api` hacia `http://127.0.0.1:8000`, así que normalmente **no necesitas** configurar `VITE_API_URL`.

Si despliegas frontend y backend en dominios distintos, puedes crear `frontend/.env`:

```env
VITE_API_URL=https://TU_BACKEND
```

## Funcionamiento del sistema

### Autenticación y roles

- Autenticación con **JWT**.
- Endpoints principales de auth:
  - `POST /api/auth/login/` (obtiene `access` y `refresh`)
  - `POST /api/auth/token/refresh/` (renueva `access`)
  - `POST /api/auth/registro/` (crea usuario; rol inicial: **Voluntario**)
  - `GET /api/auth/yo/` (perfil actual)

Roles (según permisos):

- **Voluntario**: puede consultar inventario y registrar movimientos.
- **Coordinador**: además puede gestionar (CRUD) productos y exportar.
- **Administrador**: además puede administrar usuarios/roles.

### Inventario (Productos)

- Modelo `Producto`: nombre, código de barras (opcional), cantidad (stock) y fecha de vencimiento.
- Endpoints:
  - `GET /api/productos/` (listado)
  - `POST /api/productos/` (crear; requiere rol coordinador/admin)
  - `GET /api/productos/<id>/` (detalle)
  - `PATCH/PUT/DELETE /api/productos/<id>/` (editar/borrar; requiere rol coordinador/admin)

### Movimientos (Entradas/Salidas)

- Modelo `Movimiento`: referencia a producto, tipo (`entrada`/`salida`), cantidad, nota, usuario.
- Endpoint:
  - `GET /api/movimientos/` (historial)
  - `POST /api/movimientos/` (crea movimiento y **actualiza stock** en transacción)

Reglas clave:

- Una **salida** no puede dejar stock negativo (valida stock disponible).

### Alertas, Dashboard y estructuras

- `GET /api/dashboard/`: resumen (total productos, con stock, alertas próximas).
- `GET /api/alertas/`: productos con stock que vencen en ≤ 7 días.
- `GET /api/cola-prioridad/`: productos con stock ordenados por vencimiento (min-heap).

Vista pública (sin login):

- `GET /api/publico/estructuras/`: devuelve métricas y top de cola de prioridad + estadísticas de tabla hash basadas en el inventario real.

### Búsqueda por código de barras

- `POST /api/buscar-codigo/` con `{ "codigo_barras": "..." }`.
- Usa un índice hash en memoria construido desde el catálogo actual.

Códigos DEMO (si ejecutaste el seed):

- `DEMO-BA-0003`, `DEMO-BA-0007`, `DEMO-BA-0011`

### Exportación

- `GET /api/exportar/excel/` (requiere coordinador/admin)
- `GET /api/exportar/pdf/` (requiere coordinador/admin)

## Troubleshooting rápido

- **No conecta a MySQL**: revisa credenciales en `backend/.env` y que la base exista.
- **Permiso denegado en la UI**: asegúrate de ejecutar `python manage.py promover_admin TU_USUARIO`.
- **Frontend no llega al backend**: confirma que el backend corre en 8000 y que Vite proxy está activo (`npm run dev`).
