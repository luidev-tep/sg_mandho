# Control de Versiones de Base de Datos — Flyway (`backend/db/`)

Este directorio gestiona la evolución versionada del esquema T-SQL de `sg_mandho` sobre **SQL Server 2022** y **Azure SQL Database** sin necesidad de un ORM.

## Estructura y Convenciones

```text
backend/db/
├── flyway.toml                              # Configuración base de Flyway (baselineOnMigrate = true)
├── README.md
└── migrations/
    ├── V1__initial_schema.sql               # 11 tablas (DIM_* y FACT_Revenue) + 5 índices
    ├── V2__seed_core_catalogs.sql           # Catálogos maestros idempotentes (Roles, Status, Services, Movements)
    ├── V3__harden_revenue_and_utc_defaults.sql  # CHECK (amount >= 0) y SYSUTCDATETIME() en timestamps
    ├── R__views_security_and_clients.sql    # Vistas repetibles: SecurityUsers, VISTA_CLIENTES_ACTIVOS
    └── R__views_payments.sql                # Vistas repetibles: VISTA_PAGOS_* y VISTA_PAGOS_DETALLADO_*
```

### Reglas de Oro
1. **Migraciones versionadas (`V<N>__descripcion.sql`)**: Se ejecutan una sola vez en orden estricto. **Nunca modifiques** una migración `V*` que ya fue aplicada en algún entorno; crea una nueva `V<N+1>__...`.
2. **Migraciones repetibles (`R__descripcion.sql`)**: Flyway recalcula su checksum SHA-256 en cada ejecución y las vuelve a aplicar automáticamente cuando cambian. Ideales para vistas (`CREATE OR ALTER VIEW`), funciones o procedimientos almacenados.
3. **Nunca subir credenciales**: Si necesitas parámetros locales, colócalos en `backend/db/flyway.local.toml` (ignorado por `.gitignore`) o pásalos por variables de entorno (`FLYWAY_URL`, `FLYWAY_USER`, `FLYWAY_PASSWORD`).

---

## Ejecución según Entorno

### 1. Docker Compose (Desarrollo local recomendado)
Levanta SQL Server y ejecuta las migraciones con el perfil `migrate`:

```powershell
# 1) Levantar SQL Server en segundo plano
docker compose -f docker-compose.db.yml up -d sqlserver

# 2) Aplicar migraciones Flyway
docker compose -f docker-compose.db.yml --profile migrate run --rm flyway migrate

# 3) Ver estado e historial de migraciones
docker compose -f docker-compose.db.yml --profile migrate run --rm flyway info
```

### 2. SQL Server Express Local (Windows `localhost\SQLEXPRESS`)
> **Nota importante sobre puertos dinámicos**: Si el servicio `SQL Browser` está detenido en Windows, JDBC no puede resolver el nombre de instancia `\SQLEXPRESS` y requiere el puerto TCP dinámico actual (por ejemplo `50255`).

```powershell
# Consultar el puerto TCP en escucha de sqlservr.exe
Get-NetTCPConnection -State Listen | Where-Object { (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName -eq 'sqlservr' }

# Ejecutar Flyway CLI contra SQLEXPRESS (reemplaza el puerto si cambió)
flyway -configFiles=backend/db/flyway.toml `
  -url="jdbc:sqlserver://localhost:50255;databaseName=sg_mandho;encrypt=false;trustServerCertificate=true" `
  -user="<TU_USUARIO_SQL>" `
  -password="<TU_PASSWORD>" `
  migrate
```

*(Si una base existente ya tenía las tablas creadas antes de adoptar Flyway, `baselineOnMigrate = true` con `baselineVersion = "1"` registra la línea base automáticamente en `flyway_schema_history` y aplica de `V2` en adelante.)*

### 3. Azure SQL Database (Producción / Demo)
```powershell
flyway -configFiles=backend/db/flyway.toml `
  -url="jdbc:sqlserver://<TU_SERVIDOR>.database.windows.net:1433;databaseName=sg_mandho;encrypt=true;trustServerCertificate=false" `
  -user="<ADMIN_AZURE_SQL>" `
  -password="<PASSWORD_AZURE_SQL>" `
  migrate
```
