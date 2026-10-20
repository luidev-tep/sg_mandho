# S.G. El Mandhó — Sistema de Gestión Comunitaria

Sistema web para la administración de una delegación comunitaria: gestión de vecinos, cuentas, pagos de servicios (agua, feria, panteón, delegación), cortes de caja y reportes analíticos.

Primer proyecto real del equipo de desarrollo, construido en equipo aplicando POO y arquitectura modular.

## Arquitectura general

Aplicación de dos capas que se comunican vía REST:

```
┌─────────────────────┐         ┌──────────────────────────┐        ┌──────────────┐
│  Frontend SPA       │  HTTP/  │  Backend API Flask       │  SQL   │  SQLite      │
│  React 19 + Vite    │ ──────► │  Blueprints + JWT        │ ─────► │  (modelo     │
│  Tailwind v4        │  axios  │  (JWT-Extended + CORS)   │        │   estrella)  │
└─────────────────────┘         └──────────────────────────┘        └──────────────┘
```

- **Frontend**: SPA React con enrutado, contexto de autenticación, formularios validados (yup), gráficas Chart.js y diseño responsivo. Ver `frontend/README.md`.
- **Backend**: API Flask con 7 blueprints, autenticación/autorización JWT por roles (delegado, subdelegado, comitiva), capa CRUD orientada a objetos sobre SQLite con modelo estrella. Ver `backend/README.md`.
- **Base de datos**: esquema dimensional (tabla de hechos `FACT_Revenue` + dimensiones `DIM_*`) documentado en `backend/Data_Base_Schema.sql`.

## Estructura del repositorio

```
sg_mandho/
├── backend/               # API Flask (Python, OOP, SQLite, JWT)
│   ├── app.py             # Configuración de la app, blueprints, CORS
│   ├── Data_Base_Schema.sql
│   ├── initial_information.sql
│   ├── Procfile           # gunicorn para despliegue
│   ├── src/               # rutas, CRUDs, repositorios, utilidades, tests
│   └── public/            # diagramas
├── frontend/              # SPA React 19 + Vite + Tailwind v4
│   └── src/               # páginas, componentes, capa api, utils
└── *.svg                  # diagramas de clases y paquetes del backend
```

## Roles del sistema

| Rol | Alcance |
|---|---|
| **Delegado** | Acceso completo: personas, cuentas, pagos, analíticas, administradores |
| **Subdelegado** | Administración restringida a su manzana (fracción) |
| **Comitiva** | Solo su servicio asignado (água, feria, panteón, delegación): pagos, corte de caja, servicios |

##flujo de autenticación

1. `POST /api/security/login/` emite *access token* (20 min) y *refresh token* (1 día).
2. El frontend guarda los tokens (expiración local: 24 h) y refresca proactivamente cada 15 min.
3. El decorador `@role_required` valida el rol en los claims del JWT en cada endpoint protegido.
4. Acciones sensibles exigen revalidar la contraseña (`/security/validate_password/`).

## Puesta en marcha

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Crear .env con: SECRET_KEY, URL_FRONTEND (orígenes CORS separados por coma)
python app.py     # http://127.0.0.1:5000
```

Variables de entorno: `SECRET_KEY` (obligatoria), `URL_FRONTEND`.

### Frontend

```powershell
cd frontend
pnpm install
# Crear .env con: VITE_API_URL, VITE_RECAPTCHA_SITE_KEY, VITE_ENVIRONMENT
pnpm dev          # http://localhost:5173
```

## Documentación detallada

- `backend/README.md` — arquitectura, esquema de datos, endpoints API, clases y dependencias.
- `frontend/README.md` — stack, estructura de carpetas, rutas, capa API y autenticación.
- `backend/database/schema_documentation.txt` — esquema extraído por PRAGMA.
- `docs/migracion_sqlserver.md` — plan de migración SQLite → SQL Server, pool de conexiones y entorno local.
- Diagramas UML en `*.svg` (raíz) y `backend/public/`.
