# Migración de SQLite a SQL Server (Azure SQL) + pool de conexiones

> **Histórico — Migración completada (ver `bitacora_tecnica_migracion_sqlserver.md` y `backend/db/`).**

## 1. Objetivo

1. Migrar el motor de SQLite a SQL Server / Azure SQL para eliminar los bloqueos de
   escritura en producción y la pérdida de datos en despliegues sin volumen persistente.
2. Resolver de una vez la ineficiencia de conexiones: hoy cada operación abre y cierra
   su propia conexión (31 archivos usan `Conexion`, 67 llamadas `.execute()`).
3. Dejar preparado el entorno local para desarrollar y probar la migración.

No incluye cambios de frontend: la SPA solo apunta a `VITE_API_URL`.

---

## 2. Inventario: archivos que se tocan

### 2.1 Núcleo de conexión

| Archivo | Cambio |
|---|---|
| `backend/src/utils/conexion.py` | Reescritura completa: driver `pyodbc` + pool de SQLAlchemy. Se conserva la API pública (`cursor`, `save_changes`, `close_conexion`, `conexion`, `get_route`) para no tocar los 31 archivos que la consumen. |

### 2.2 Archivos que importan `sqlite3` (23)

Todos cambian `import sqlite3` por `import pyodbc` y `sqlite3.Error` por `pyodbc.Error`
(~49 referencias a `sqlite3.Error` en total):

```
backend/src/accounts/services/validate.py
backend/src/dim_dates/dim_date.py
backend/src/dim_roles/repository/show.py
backend/src/dim_servicedetails/repository/create.py
backend/src/dim_servicedetails/repository/show.py
backend/src/dim_servicedetails/repository/update.py
backend/src/dim_serviceonwers/repository/show.py
backend/src/dim_status/status.py
backend/src/fact_revenues/repository/edit.py
backend/src/fact_revenues/repository/insert.py
backend/src/payments/repository/cash_cut_querys.py
backend/src/payments/repository/get_fact_revenues_customer.py
backend/src/payments/repository/get_pending_pays.py
backend/src/payments/repository/read_payments.py
backend/src/payments/services/validate_payment.py
backend/src/security/repository/get_onwers_info.py
backend/src/security/repository/user_info.py
backend/src/users/repository/create.py
backend/src/users/repository/delete.py
backend/src/users/repository/edit.py
backend/src/users/repository/home_info.py
backend/src/users/repository/show.py
backend/src/utils/conexion.py
```

Los demás módulos (`accounts/*`, `payments/*`, `analytics_reports/*`, etc.) consumen
`Conexion` sin importar `sqlite3`; no requieren cambio en Fase 1.

### 2.3 Esquema y datos

| Archivo | Cambio |
|---|---|
| `backend/Data_Base_Schema.sql` | Reescritura a T-SQL: tipos, `DEFAULT` de timestamps, corrección de la FK sin coma en `DIM_CashCut` (~L146) y vistas. |
| `backend/initial_information.sql` | Revisión de seeds: literales Unicode con `N'...'`, tipos y orden de inserción. |
| `backend/database/schema.py` | Herramienta 100% SQLite (`sqlite_master`, `PRAGMA`). Se retira o se reescribe para SQL Server (`INFORMATION_SCHEMA`). |
| `backend/database/schema_documentation.txt` / `.json` | Regenerar con la herramienta nueva. |
| `backend/database/sistema_mandho.db` | Solo como origen de la migración de datos y de las vistas (ver 2.5). |

### 2.4 Configuración, dependencias y despliegue

| Archivo | Cambio |
|---|---|
| `backend/.env` y `backend/.env.example` | Sustituir `DATABASE_PATH` (hoy ignorado por `Conexion`) por `DB_DRIVER`, `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`. |
| `backend/requirements.txt` | Agregar `pyodbc`. `SQLAlchemy==2.0.40` ya está y pasa a usarse (hoy está sin uso). |
| `Dockerfile` (nuevo, `backend/`) | Imagen con `msodbcsql18` + gunicorn. Base para Container Apps. |
| `docker-compose.yml` (nuevo, raíz) | SQL Server Developer local para desarrollo. |
| `backend/app.py` | Sin cambios de código; solo cambian variables de entorno. |

### 2.5 Vistas: el `.db` vivo no coincide con el SQL

`Data_Base_Schema.sql` solo define 3 vistas (`VISTA_PAGOS_AGUA`, `VISTA_PAGOS_FERIA`,
`VISTA_CLIENTES_ACTIVOS`), pero la base viva tiene **10 vistas**:

```
SecurityUsers                        -- usada por login/roles; NO está en el SQL del repo
VISTA_CLIENTES_ACTIVOS
VISTA_PAGOS_AGUA
VISTA_PAGOS_DELEGACION
VISTA_PAGOS_DETALLADO_AGUA
VISTA_PAGOS_DETALLADO_DELEGACION
VISTA_PAGOS_DETALLADO_FERIA
VISTA_PAGOS_DETALLADO_PANTEON
VISTA_PAGOS_FERIA
VISTA_PAGOS_PANTEON
```

Antes de reescribir el DDL hay que **extraer las 10 vistas del `.db` vivo**:

```python
import sqlite3
conn = sqlite3.connect("database/sistema_mandho.db")
for name, sql in conn.execute(
    "SELECT name, sql FROM sqlite_master WHERE type='view' ORDER BY name"
):
    print(f"-- {name}\n{sql};\nGO\n")
conn.close()
```

### 2.6 Puntos de SQL con dialecto SQLite

| Ubicación | SQLite | T-SQL |
|---|---|---|
| `backend/src/routes/search_real_time.py:135` | `LIMIT 50` | `SELECT TOP 50 ...` u `OFFSET/FETCH` |
| `backend/src/users/repository/home_info.py:18` | `a \|\| ' ' \|\| b` | `CONCAT(a, ' ', b)` o `a + ' ' + b` |
| `backend/src/analytics_reports/repository/get_analytics.py:185` | `IFNULL(SUM(...), 0)` | `ISNULL(SUM(...), 0)` |
| `backend/src/analytics_reports/repository/PaymentProcesor.py:56` | `strftime(Year)` | Revisar: parece un bug (pasa una columna como formato). En T-SQL sería `CAST(... AS ...)`. |
| `backend/Data_Base_Schema.sql:299` | `strftime('%Y', StartDate)` | `YEAR(StartDate)` o `FORMAT(StartDate, 'yyyy')` |
| `backend/Data_Base_Schema.sql` (vistas) | `GROUP BY 1,2,3...` (ordinales) | T-SQL **no** soporta ordinales: repetir expresiones o usar subconsulta |
| `backend/Data_Base_Schema.sql` (vistas) | `CAST(x AS TEXT)` | `CAST(x AS VARCHAR/NVARCHAR(50))` |
| `backend/Data_Base_Schema.sql` (11 tablas) | `DEFAULT strftime('%Y-%m-%d %H:%M:%S','now','localtime')` | `DEFAULT` con `SYSDATETIME() AT TIME ZONE` o `GETDATE()` (ver §3) |
| `backend/src/utils/conexion.py:72,75` | `PRAGMA journal_mode=WAL`, `busy_timeout` | Se eliminan (no aplican) |

No hay `AUTOINCREMENT` ni `lastrowid` en el código: los IDs son TEXT generados por
`create_id` (UUID5) y `DIM_DateId` es un entero asignado por la app. Eso simplifica el DDL.

---

## 3. Mapeo de dialecto SQLite → T-SQL

| Tema | SQLite | SQL Server / T-SQL |
|---|---|---|
| Placeholders | `?` | `?` con `pyodbc` (qmark) — **no cambian** |
| Texto | `TEXT` | `NVARCHAR(n)` / `NVARCHAR(MAX)`; literales `N'...'` |
| Enteros | `INTEGER` | `INT` / `BIGINT` |
| Decimales | `REAL` | `DECIMAL(10,2)` (más seguro para dinero) o `FLOAT` |
| Fechas en tablas | `TEXT` ('YYYY-MM-DD') | `DATE` / `DATETIME2` (evaluar impacto en serialización) |
| `DIM_DateId` | `INTEGER` AAAAMMDD | `INT` sin cambio |
| Fecha actual | `datetime('now')` | `SYSDATETIME()` (UTC) o `AT TIME ZONE 'Central Standard Time'` |
| Concat | `\|\|` | `+` o `CONCAT()` |
| Nulos | `IFNULL` | `ISNULL` / `COALESCE` |
| Límite | `LIMIT` | `TOP` / `OFFSET-FETCH` |
| `GROUP BY` ordinal | soportado | **no** soportado |
| Case en `LIKE` | case-insensitive | case-insensitive con collation por defecto (a favor) |
| Booleanos | `0/1` | `BIT` (pyodbc devuelve `True/False`) |
| Errores | `sqlite3.Error` | `pyodbc.Error` |
| Upsert | `ON CONFLICT` | `MERGE` |
| Timestamps DEFAULT | `strftime(...)` | `DEFAULT (SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time')` |

Riesgo conocido: `pyodbc` devuelve objetos `datetime`/`Decimal`; si se cambian columnas
de `TEXT` a `DATE`, hay que revisar los sitios que hoy concatenan o comparan strings.

---

## 4. Fase 1 — Pool de conexiones (resuelve la ineficiencia)

### Problema actual

- Cada operación hace `Conexion()` → `connect` + 2 PRAGMA → `execute` → `close`.
  Con SQL Server eso es un handshake TCP+TLS+login por consulta (20–100 ms).
- `insert_new_Onwer` abre 3 conexiones independientes (`insert_account`,
  `update_user_info`, `insert_service_owner_info`): si falla la última, quedan datos
  parciales (no hay transacción real).
- Azure SQL Basic limita sesiones concurrentes; sin pool, un pico agota el límite.

### Solución: reescribir solo `backend/src/utils/conexion.py`

Se mantiene la API para no tocar los 31 consumidores. Esbozo:

```python
import os
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        driver = os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={os.environ['DB_SERVER']};"
            f"DATABASE={os.environ['DB_NAME']};"
            f"UID={os.environ['DB_USER']};"
            f"PWD={os.environ['DB_PASSWORD']};"
            "Encrypt=yes;TrustServerCertificate=no;"
        )
        _engine = create_engine(
            "mssql+pyodbc:///?odbc_connect="
            + urllib.parse.quote_plus(connection_string),
            poolclass=QueuePool,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "10")),
            pool_pre_ping=True,   # descarta conexiones muertas
            pool_recycle=1800,    # recicla cada 30 min
        )
    return _engine


class Conexion:
    """Conexión obtenida del pool. `close_conexion()` la devuelve, no la destruye."""

    def __init__(self) -> None:
        self.conn = _get_engine().raw_connection()
        self.cursor = self.conn.cursor()

    def get_route(self) -> str:
        return f"{os.environ['DB_SERVER']}/{os.environ['DB_NAME']}"

    def save_changes(self) -> None:
        self.conn.commit()

    def conexion(self) -> tuple:
        return self.conn, self.cursor

    def close_conexion(self) -> None:
        # Al devolver la conexión al pool, SQLAlchemy hace rollback de lo no commiteado.
        self.cursor.close()
        self.conn.close()
```

Detalles:

- `save_changes()` sigue siendo el único punto de commit → semántica idéntica a hoy.
- `close_conexion()` ya no cierra la conexión física; la regresa al pool (rollback si
  faltó commit).
- `pyodbc` + SQLAlchemy usan el ODBC Driver 18; en Azure SQL hay que decidir
  `Encrypt`/`TrustServerCertificate` según el certificado.
- Si en el futuro se usa PostgreSQL, esta misma clase cambia la URL a
  `postgresql+psycopg://` y opcionalmente el puerto 6432 (PgBouncer del propio Azure).
- Variables nuevas: `DB_POOL_SIZE` (default 5), `DB_MAX_OVERFLOW` (default 10).

### Resultado esperado

- 1 conexión física por worker/thread reutilizada durante toda la vida del proceso.
- Latencia por consulta: de ~20–100 ms de handshake a microsegundos.
- Las consultas leen/escriben concurrentemente sin `database is locked`.

### Medición antes/después (recomendada)

Pequeño script de benchmark (ej. 100 llamadas a `get_securyty_users_info()` con y sin
pool) para dejar registro del antes/después en este mismo documento.

---

## 5. Fase 2 — Una conexión por request y transacciones (recomendada, opcional)

Objetivo: además del pool, dejar de abrir conexiones múltiples dentro del mismo flujo.

1. Conexión por request con Flask `g`:

```python
@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close_conexion()
```

2. Añadir a `Conexion` soporte de context manager (`__enter__`/`__exit__`) y usarlo en
   los flujos multi-paso:

```python
def insert_onwer_info(data: dict) -> tuple[int, str]:
    with Conexion() as db:
        estado, mensaje = handler_account.insert_account(data_for_account, db)
        if estado != 200:
            db.rollback()  # o dejar que __exit__ haga rollback
            return estado, mensaje
        estado, mensaje = update_user_info(..., db)
        ...
        db.commit()
```

3. Pasar la conexión a `insert_account`, `update_user_info` e `insert_service_owner_info`
   (hoy cada una construye la suya y commitea por separado).

Beneficio: atomicidad real en alta de administradores y cortes de caja, y menos
round-trips por operación.

---

## 6. Fase 3 — Esquema y datos

1. Extraer las 10 vistas del `.db` vivo (§2.5).
2. Reescribir `Data_Base_Schema.sql` a T-SQL aplicando la tabla §3 y corrigiendo la FK
   sin coma de `DIM_CashCut`.
3. Reescribir seeds de `initial_information.sql` con `N'...'` y tipos correctos.
4. Migrar datos con un script (mismo orden de dependencias FK):

```python
import sqlite3
import pyodbc

TABLES = [
    "DIM_Role", "DIM_Status", "DIM_Date", "DIM_Customer", "DIM_Account",
    "DIM_Service", "DIM_ServiceDetails", "DIM_ServiceOwners", "DIM_Movement",
    "FACT_Revenue", "DIM_CashCut",
]

src = sqlite3.connect("database/sistema_mandho.db")
dst = pyodbc.connect("DRIVER={ODBC Driver 18 for SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...;TrustServerCertificate=yes")

for table in TABLES:
    rows = src.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        continue
    cols = len(rows[0])
    placeholders = ",".join("?" * cols)
    dst.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    print(f"{table}: {len(rows)} filas")

dst.commit()
```

5. Validar conteos `SELECT COUNT(*)` por tabla en ambos motores.

---

## 7. Entorno local (paso a paso)

### Requisitos

- Python 3.13 (venv ya existe en `backend/venv`).
- Node 22 + pnpm 10.
- Docker Desktop (recomendado) o SQL Server LocalDB en Windows.

### Opción A — SQL Server en Docker (recomendada)

`docker-compose.yml` (raíz del repo):

```yaml
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: sg_mandho_sqlserver
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_PID: Developer
      MSSQL_SA_PASSWORD: "${MSSQL_SA_PASSWORD:?define MSSQL_SA_PASSWORD}"
    ports:
      - "1433:1433"
    volumes:
      - sqlserver_data:/var/opt/mssql
      - ./backend/sql:/scripts

volumes:
  sqlserver_data:
```

```powershell
# 1. Definir password fuerte (mín. 8 chars, mayúscula, minúscula, número y símbolo)
$env:MSSQL_SA_PASSWORD = Read-Host 'SQL Server SA password'
docker compose up -d

# 2. Ejecutar esquema y seeds (la imagen 2022 trae sqlcmd en mssql-tools18)
docker exec -it sg_mandho_sqlserver /opt/mssql-tools18/bin/sqlcmd `
  -S localhost -U sa -P "$env:MSSQL_SA_PASSWORD" -C -i /scripts/01_schema.sql
docker exec -it sg_mandho_sqlserver /opt/mssql-tools18/bin/sqlcmd `
  -S localhost -U sa -P "$env:MSSQL_SA_PASSWORD" -C -i /scripts/02_seed.sql
```

Nota Apple Silicon: la imagen oficial de SQL Server es `amd64`; Docker Desktop la emula
(lenta) o se usa una VM/equipo x64.

### Opción B — Azure SQL free tier como BD de desarrollo

- Crear una BD serverless en el tier gratuito (100k vCore-s + 32 GB/mes).
- Agregar tu IP pública al firewall del servidor.
- Usar `DB_SERVER=<server>.database.windows.net,1433` y `Encrypt=yes`.
- Ventaja: no consumes RAM local y pruebas el motor real de producción.

### Configuración del backend

`backend/.env` (local, no se commitea):

```env
SECRET_KEY=<64 hex generados con: python -c "import secrets; print(secrets.token_hex(32))">
URL_FRONTEND=http://localhost:5173,https://<frontend-prod>
RECAPTCHA_ENABLED=false
RECAPTCHA_SECRET_KEY=

DB_DRIVER=ODBC Driver 18 for SQL Server
DB_SERVER=localhost,1433
DB_NAME=sg_mandho
DB_USER=sa
DB_PASSWORD=<SQL_SERVER_PASSWORD>
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

`backend/requirements.txt`: agregar `pyodbc` y reinstalar:

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend (sin cambios)

```env
VITE_API_URL=http://127.0.0.1:5000/api/
VITE_RECAPTCHA_SITE_KEY=<site key>
VITE_ENVIRONMENT=development
```

```powershell
cd frontend
pnpm install
pnpm dev   # http://localhost:5173
```

### Verificación

1. `.\venv\Scripts\python.exe app.py` inicia sin error de `SECRET_KEY`.
2. Login contra `/api/security/login/` con `RECAPTCHA_ENABLED=false`.
3. `pytest src/test -v`: la suite ya tenía **20 fallos por datos** antes de la migración
   (estado de la BD de desarrollo); la meta es no aumentar ese número.
4. `pnpm build` en frontend sin errores.

### Gotchas del repo (ya conocidos)

- Un clon nuevo **no trae** `backend/database/sistema_mandho.db` (`database/` está en
  `.gitignore`); con SQL Server esto deja de importar.
- `URL_FRONTEND` debe incluir `http://localhost:5173` o el navegador falla por CORS.
- `DATABASE_PATH` del `.env` actual no lo usa nadie (`Conexion` deriva la ruta).
- Erratas heredadas que **no** se tocan por compatibilidad: `Singup.jsx`, `gat_data`,
  `ServiceDetailesType`, `DIM_ServiceOnwers`.

---

## 8. Despliegue Azure (referencia)

| Componente | Servicio | Costo aprox. |
|---|---|---|
| Frontend | Static Web Apps Free | $0 (100 GB/mes, 2 dominios) |
| Backend | Container Apps Consumption (scale-to-zero) | $0–6 USD/mes |
| BD | Azure SQL Database free tier (serverless) o Basic 5 DTU | $0 o ~$5 USD/mes |
| BD alternativa | Azure SQL Basic: 2 GB máx, 5 DTU | riesgo de throttling con analíticas |
| Imagen | ghcr.io (GitHub) | $0; ACR Basic +$5 USD/mes |
| **Total** | | **~$0–11 USD/mes** |

Advertencia: con Basic (5 DTU / 2 GB) el dashboard de analíticas puede provocar
throttling (errores 10928/40501). El tier gratuito serverless da 32 GB y pausa sola.

---

## 9. Estimación y riesgos

| Fase | Esfuerzo |
|---|---|
| Pool en `conexion.py` (Fase 1) | 2–3 jornadas |
| Conexión por request + transacciones (Fase 2) | 8–12 jornadas |
| Esquema T-SQL + 10 vistas + seeds | 4–6 jornadas |
| Migración de datos + validación | 2–3 jornadas |
| Correcciones de dialecto (§2.6) | 3–5 jornadas |
| Driver, `.env`, Dockerfile/compose | 2 jornadas |
| Tests y regresión de endpoints | 3–5 jornadas |
| **Total** | **24–36 jornadas** (sin Fase 2: 16–24) |

Riesgos principales:

1. **El `.db` vivo es la fuente de verdad**: el SQL del repo está desactualizado
   (10 vistas vs 3, FK sin coma). Extraer DDL antes de reescribir.
2. **Fechas**: cambiar `TEXT` a `DATE`/`DATETIME2` altera serialización en respuestas.
   Alternativa conservadora: mantener `NVARCHAR` para fechas en la primera iteración.
3. **`PaymentProcesor.py:56`** (`strftime(Year)`) parece un bug latente; verificar
   comportamiento actual antes de traducir.
4. **ODBC en contenedor**: el Dockerfile necesita `msodbcsql18`.
5. **Tests**: la suite actual ya es parcialmente dependiente del estado de la BD;
   definir una BD de pruebas limpia (contenedor efímero por corrida).

---

## 10. Checklist de aceptación

- [ ] Las 10 vistas del `.db` extraídas y creadas en T-SQL.
- [ ] `Data_Base_Schema.sql` y `initial_information.sql` ejecutan limpios en SQL Server.
- [ ] Conteos de filas idénticos entre SQLite y SQL Server.
- [ ] `Conexion` usa pool; sin `connect/close` por operación.
- [ ] Login, pagos, corte de caja, analíticas y búsqueda funcionan end-to-end.
- [ ] `pytest src/test` no supera los 20 fallos preexistentes.
- [ ] `pnpm build` sin errores.
- [ ] Sin secretos en el repo (`.env` ignorado, `.env.example` actualizado).
