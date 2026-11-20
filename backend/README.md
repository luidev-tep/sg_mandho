# Backend — SG Mandhò

API REST con Flask para administrar personas, cuentas, pagos, cortes de caja y analíticas comunitarias. La persistencia usa SQL Server mediante `pyodbc`; el modelo dimensional incluye `FACT_Revenue` y diez tablas `DIM_*`. Azure Container Apps ejecuta la API en producción/demo y Azure SQL Database hospeda la base de datos.

## Stack y arquitectura

- Python 3.13, Flask, Flask-JWT-Extended y Gunicorn.
- SQL Server / Azure SQL mediante `pyodbc` y SQLAlchemy `QueuePool`.
- Repositorios y servicios organizados por módulo: ruta → CRUD/servicio → repositorio SQL → modelo.
- Migraciones T-SQL administradas con Flyway en `backend/db/`.
- Despliegue de contenedor definido en `Dockerfile`, con ODBC Driver 18, usuario no-root y `HEALTHCHECK` a `/health`.

### Módulos principales

| Módulo | Responsabilidad |
|---|---|
| `src/routes/` | Endpoints Flask y validación de entrada |
| `src/security/` | Autenticación, contraseñas y autorización por rol |
| `src/users/`, `src/accounts/` | Padrón, cuentas y vigencias |
| `src/payments/`, `src/fact_revenues/` | Pagos, facturación y cortes de caja |
| `src/analytics_reports/` | Consultas analíticas y reportes |
| `src/utils/conexion.py` | Conexión, pool y unidades de trabajo |

## Persistencia y transacciones

El modelo contiene 11 tablas: `FACT_Revenue`, diez dimensiones `DIM_*` y diez vistas T-SQL para seguridad, clientes activos y pagos por servicio. Los nombres y definiciones vigentes están en `backend/db/migrations/`.

`Conexion` obtiene conexiones de `QueuePool`. Los repositorios parametrizan sus valores SQL. Los flujos que requieren atomicidad comparten la misma conexión con `with Conexion() as tx:` y confirman el trabajo explícitamente antes de salir del contexto. Las conexiones se devuelven al pool en `finally` o al cerrar el context manager.

Las contraseñas nuevas usan scrypt. Cuando un login válido encuentra un hash MD5 heredado, lo reemplaza progresivamente por un hash seguro. JWT access/refresh tokens y el decorador `role_required` restringen endpoints por rol; las comitivas también quedan limitadas a su servicio. reCAPTCHA v2 se configura con variables de entorno.

## Configuración local

Usa `backend/.env.example` como base y crea `backend/.env` local. Configura al menos:

- `SECRET_KEY`: clave aleatoria para firmar tokens.
- `URL_FRONTEND`: origen o lista de orígenes permitidos por CORS.
- `DB_DRIVER`, `DB_SERVER`, `DB_NAME` y las variables de autenticación de SQL Server (`DB_USER`, `DB_PASSWORD` o conexión confiable).
- En Azure, la identidad administrada se puede habilitar con `DB_AUTHENTICATION=ManagedIdentity`; para una identidad asignada por el usuario, define `AZURE_CLIENT_ID` y omite `DB_USER`/`DB_PASSWORD`.
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` y `DB_POOL_TIMEOUT` para dimensionar el pool.
- `RECAPTCHA_ENABLED` y `RECAPTCHA_SECRET_KEY`.

`DATABASE_PATH` era parte de la configuración SQLite heredada y no configura la conexión SQL Server actual. No guardes secretos reales en archivos versionados.

Para la guía de Docker local, Flyway, datos demo y ejecución de ambos servicios, sigue la [puesta en marcha del README raíz](../README.md#puesta-en-marcha-rápida). La guía de despliegue está en [docs/guia_despliegue_azure.md](../docs/guia_despliegue_azure.md).

## API

Los blueprints se registran en `app.py`. La API cubre:

- `/api/security/`: login, refresh y revalidación de contraseña para acciones críticas.
- `/api/user/` y `/api/account/`: padrón y cuentas.
- `/api/payment/`: pagos, costos, servicios y cortes de caja.
- `/api/analitycs/`: reportes analíticos.
- `/api/search/` y `/api/home/`: búsqueda y datos de inicio.

`GET /health` informa disponibilidad de la API y del acceso a la base de datos. Los contratos y detalles de autorización se encuentran en los blueprints de `src/routes/`.

## Desarrollo y pruebas

Desde la raíz del repositorio:

~~~powershell
.\backend\venv\Scripts\python.exe -m pytest backend\src\tests_e2e -v
~~~

La suite E2E requiere una instancia accesible de SQL Server y una base de pruebas con sus fixtures. Verifica concurrencia, reutilización física de conexiones, transacciones, consultas T-SQL, flujos API y ausencia de fugas del pool. No apunta a SQLite ni debe ejecutarse sobre datos de producción.

Para preparar cuentas y datos sintéticos de una demo, se puede usar `backend/scripts/seed_demo_azure.py` con `DEMO_ADMIN_PASSWORD`; consulta la guía Azure antes de conectar una base compartida.

## Documentación

- [Migraciones Flyway](db/README.md)
- [Guía de despliegue Azure](../docs/guia_despliegue_azure.md)
- [Bitácora técnica SQL Server](../docs/bitacora_tecnica_migracion_sqlserver.md)
