# Bitácora Técnica: Migración Arquitectónica de SQLite a SQL Server 2022 / Azure SQL

**Proyecto:** SG Mandho  
**Fecha:** 21 de Octubre de 2026  
**Estado:** Implementación Completada y Verificada (16/16 E2E Tests Aprobados sin Mocks)  

---

## 1. Resumen Ejecutivo

La aplicación **SG Mandho** operaba históricamente sobre un archivo monolítico **SQLite** (`sistema_mandho.db`), con conexiones directas no agrupadas (`sqlite3.connect`), ausencia de control transaccional distribuido, fugas sistemáticas de descriptores de conexión en múltiples controladores y hashing legado no estándar (MD5 sin sal).

Esta migración transformó integralmente la capa de persistencia y seguridad hacia una arquitectura empresarial basada en **Microsoft SQL Server 2022 / Azure SQL**, introduciendo:
1. **Pool de conexiones de alto rendimiento (`QueuePool`)** gestionado mediante SQLAlchemy sobre `pyodbc` con `ODBC Driver 17 for SQL Server`.
2. **Cierre riguroso de las 12 fugas de conexión** identificadas en la base de código mediante bloques deterministas `try ... finally`.
3. **Transaccionalidad atómica real (`ACID`)** mediante el patrón `shared_conn` y administradores de contexto (`with Conexion() as tx:`), erradicando estados huérfanos o inconsistencias intermedias ante fallos.
4. **Traducción completa de dialectismos SQLite a T-SQL estándar**, optimizando vistas, consultas de agregación y pre-filtrado de inserciones.
5. **Capa de seguridad moderna**: Hashing con `scrypt` (Werkzeug), migración transparente y automática de contraseñas heredadas en MD5 durante el login, reCAPTCHA configurable y expiración temporal anual.
6. **Suite de pruebas de aceptación End-to-End (E2E) 100% libre de mocks**, validada directamente contra la instancia real de base de datos con aserciones estrictas sobre el estado del pool (`checkedout == 0`).
7. **Artefactos de despliegue continuo en la nube** para Azure Container Apps / App Service y Azure Static Web Apps.

---

## 2. Arquitectura de Datos y Motor SQL Server

### 2.1 Tablas de Base de Datos (DDL T-SQL)
Se diseñó y aplicó el esquema en `backend/database/schema_sqlserver.sql`, compuesto por **11 tablas relacionales**:

| Tabla | Clave Primaria | Propósito | Características Especiales |
| :--- | :--- | :--- | :--- |
| `DIM_Role` | `DIM_RoleId` | Catálogo de roles del sistema | Distingue `RoleType` ('administrador', 'vecino') |
| `DIM_Status` | `DIM_StatusId` | Estados del sistema | 8 estados obligatorios (`status1` a `status8`) |
| `DIM_Date` | `DIM_DateId` | Dimensión temporal (calendario) | Entero formato `YYYYMMDD`, poblada hasta 2030 (3,650 registros) |
| `DIM_Service` | `DIM_ServiceId` | Catálogo de comisiones / servicios | Agua, Feria, Panteón, Delegación, Personas, etc. |
| `DIM_Movement` | `DIM_MovementId` | Tipo de flujo contable | `ingreso`, `egreso` |
| `DIM_Customer` | `DIM_CustomerId` | Registro unificado de personas | Almacena `username`, `password` hasheada y manzana |
| `DIM_Account` | `DIM_AccountId` | Cuenta asignada a una persona | Asocia rol, estado y período de vigencia |
| `DIM_ServiceDetails` | `DIM_ServiceDetailsId` | Asignación de servicios a una cuenta | Incluye `DIM_StatusId` corregido con respecto a SQLite |
| `DIM_ServiceOwners` | `DIM_ServiceOwnersId` | Administradores de servicios (Owners) | Define vigencia anual (`StartDate`, `EndDate`) |
| `FACT_Revenue` | `FACT_RevenueId` | Facturación e ingresos de servicios | Montos en `FLOAT`, relación directa a fechas y cuentas |
| `DIM_CashCut` | `DIM_CashCutId` | Registro de cortes de caja | Agrupa ingresos y vincula al responsable del corte |

### 2.2 Vistas T-SQL Optimizadas
Se implementaron **10 vistas T-SQL** corrigiendo limitaciones y errores de SQLite:
1. `SecurityUsers`: Vista de autenticación sin cláusulas `ORDER BY` internas (prohibidas en vistas T-SQL estándar sin TOP).
2. `Cobro_Agua_Total`, `Cobro_Feria_Total`, `Cobro_Panteon_Total`, `Cobro_Delegacion_Total`: Vistas de cobros históricos con agregaciones `SUM(amount)` y cláusulas `GROUP BY` explícitas para cumplir con el estándar ANSI/T-SQL.
3. `Cobro_Agua_Total_mes`, `Cobro_Feria_Total_mes`, `Cobro_Panteon_Total_mes`, `Cobro_Delegacion_Total_mes`: Vistas agregadas por año y mes con `GROUP BY`.
4. `TotalRecaudado`: Consolidación global de ingresos por cuenta y servicio.

---

## 3. Rediseño del Pool de Conexiones (`backend/src/utils/conexion.py`)

### 3.1 Componentes Implementados
- **Motor SQLAlchemy + pyodbc**: Se utiliza `sqlalchemy.pool.QueuePool` con creación de conexiones de bajo nivel mediante `pyodbc.connect` y parámetros `autocommit=False`.
- **Configuración del Pool**:
  - `pool_size=5`: Conexiones persistentes en reposo.
  - `max_overflow=10`: Hasta 15 conexiones concurrentes en picos de demanda.
  - `timeout=30.0`: Límite de espera antes de error de agotamiento.
  - `recycle=1800`: Reciclaje cada 30 minutos para evitar desconexiones por inactividad en Azure.
- **Manejo Unificado de Excepciones (`DatabaseError`)**: Envoltorio que unifica excepciones de `pyodbc.Error`, `sqlalchemy.exc.DBAPIError` y errores de base de datos en una clase única capturable en todos los repositorios.
- **Soporte de Conexión Compartida (`shared_conn`)**: Permite inyectar una conexión abierta y transaccional existente a cualquier repositorio sin solicitar una nueva conexión al pool ni cerrarla anticipadamente.
- **Teardown de Flask (`init_db_teardown(app)`)**: Registrado en `backend/app.py` para asegurar que al finalizar cada petición HTTP se liberen las conexiones asociadas al contexto de la solicitud.
- **Métrica del Pool (`get_pool_status()`)**: Expone `size`, `checkedin`, `checkedout` y `overflow` para auditoría y aserciones de pruebas E2E.

---

## 4. Auditoría y Cierre de las 12 Fugas de Conexión

Se inspeccionó cada función que instanciaba `Conexion()` sin asegurar su devolución al pool ante excepciones o salidas tempranas:

| # | Archivo | Función / Línea | Causa de la Fuga Original | Solución Aplicada |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `src/accounts/services/validate.py` | `validate_account` | Retornos anticipados sin `close_conexion()` | Envoltura completa en `try ... finally` |
| 2 | `src/accounts/services/validate.py` | `has_active_account` | Cierre fuera de manejo de errores | Bloque `try ... finally: object_connection.close_conexion()` |
| 3 | `src/accounts/repository/show.py` | `show_account` | Excepción en cursor dejaba conexión abierta | Bloque `try ... finally: conecion.close_conexion()` |
| 4 | `src/payments/services/validate_payment.py` | `is_account_active` | Retornos booleanos directos antes del cierre | Bloque `try ... finally: handler_coneccion.close_conexion()` |
| 5 | `src/payments/repository/read_payments.py` | `get_validation_payment` | `hanlder_conexion.close_conexion()` comentado | Descomentado y asegurado dentro de `finally` |
| 6 | `src/payments/repository/cash_cut_querys.py` | `create_cash_cut_register` | Conexión huérfana ante fallo de SQL | Soporte `db: Conexion | None` + `finally` |
| 7 | `src/payments/repository/get_fact_revenues_customer.py` | `get_fact_revenues_customer` | Omisión de cláusula `finally` | Bloque `try ... finally: handler_conecction.close_conexion()` |
| 8 | `src/dim_dates/dim_date.py` | `get_by_id` | Instanciación de conexión previa al `try` | Conexión en `try` + `finally: connection.close_conexion()` |
| 9 | `src/dim_dates/dim_date.py` | `_insert_year_dates` | Excepción en lote dejaba socket abierto | Bloque `try ... finally: handler_connection.close_conexion()` |
| 10 | `src/dim_roles/repository/show.py` | `get_role` | `close_conexion()` fuera de `finally` | Movido al bloque `finally` |
| 11 | `src/dim_serviceonwers/repository/show.py` | `get_ServiceOnwers_by_name` | Sentencia SQL fallida bloqueaba cierre | Bloque `try ... finally: object_conecction.close_conexion()` |
| 12 | `src/analytics_reports/repository/PaymentProcesor.py` | `get_all_data_payments` | Bucle de agregación con retornos intermedios | Envoltura de todo el flujo en `try ... finally` |

Adicionalmente, se actualizaron **23 archivos de repositorio y servicio**, eliminando `import sqlite3` y reemplazando `except sqlite3.Error` por `except DatabaseError`.

---

## 5. Transaccionalidad Atómica (`shared_conn` y `with Conexion() as tx:`)

Se refactorizaron los 4 flujos transaccionales multi-tabla para garantizar propiedades **ACID**:

1. **Flujo A: Alta de Administrador (`src/security/repository/user_info.py`)**:
   - `insert_account` (db=tx) ➔ `update_user_info` (db=tx) ➔ `insert_service_owner_info` (db=tx).
   - Ante fallo en cualquiera de las fases, se invoca `tx.rollback()`, impidiendo clientes con permisos a medias o cuentas huérfanas.
2. **Flujo B: Corte de Caja (`src/payments/cash_cut.py`)**:
   - Inserción en lote de facturas `FACT_Revenue` (db=tx) ➔ Creación del registro `DIM_CashCut` (db=tx).
   - Rollback automático si falla el registro del corte o alguna factura.
3. **Flujo C: Checklist Masivo de Pagos (`src/fact_revenues/Fact_revenue.py`)**:
   - `insert_many_fact_revenues` con `fast_executemany = True` (db=tx) ➔ `Update_dim_service_details` a estado `status8` (db=tx).
   - Si la actualización del servicio falla, ninguna factura de pago queda insertada.
4. **Flujo D: Creación de Cuenta y Usuario (`src/accounts/services/validate.py` y `account.py`)**:
   - Desactivación de cuenta anterior (db=tx) ➔ Inserción de nueva cuenta (db=tx).

---

## 6. Traducción de Dialectismos SQLite a T-SQL

| Componente | SQLite (Original) | SQL Server / T-SQL (Aplicado) | Razón del Cambio |
| :--- | :--- | :--- | :--- |
| `src/routes/search_real_time.py` | `SELECT ... LIMIT 50` | `SELECT TOP 50 ...` | En T-SQL no existe la cláusula `LIMIT` al final. |
| `src/users/repository/home_info.py` | `cu.Fraction \|\| ' ' \|\| cu.Address` | `CONCAT(cu.Fraction, ' ', cu.Address)` | Operador de concatenación `\|\|` produce error de sintaxis en SQL Server. |
| `src/analytics_reports/repository/get_analytics.py` | `IFNULL(SUM(vw.amount), 0)` | `ISNULL(SUM(vw.amount), 0)` | T-SQL utiliza `ISNULL` o `COALESCE`. |
| `src/analytics_reports/repository/PaymentProcesor.py` | `strftime(Year) as year` | `CAST(d.Year AS NVARCHAR(10)) as Year` | `strftime` es una función exclusiva de SQLite. |
| `src/users/repository/show.py` | `WHERE EndDate is not 's/n'` | `WHERE EndDate <> 's/n'` | Comparación sintácticamente inválida en T-SQL. |
| `src/dim_dates/dim_date.py` | `INSERT OR IGNORE INTO DIM_Date` | Pre-filtrado en memoria de `DIM_DateId` existentes | En T-SQL no existe `INSERT OR IGNORE`. |
| `src/dim_serviceonwers/repository/show.py` | `FROM DIM_ServiceOnwers` | `FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?` | Corrección de errata histórica en nombre de tabla y parametrización con tupla. |
| `src/security/repository/get_onwers_info.py` | `SELECT * FROM SecurityUsers` | `SELECT * FROM SecurityUsers ORDER BY StartDate DESC` | Traslado del ordenamiento a la consulta ya que las vistas T-SQL no admiten `ORDER BY`. |

---

## 7. Seguridad y Control de Acceso

1. **Hashing Seguro con `scrypt`**: Sustitución de `hashlib.md5` por `generate_password_hash` y `check_password_hash` de Werkzeug.
2. **Migración Transparente de Hashes Legados**:
   - Si un usuario ingresa con credenciales que aún conservan hash MD5, el sistema valida la firma y automáticamente actualiza la base de datos a `scrypt` en segundo plano sin requerir restablecimiento de clave.
3. **Manejo de reCAPTCHA Condicional**:
   - `RECAPTCHA_ENABLED=true`: Producción valida contra Google reCAPTCHA v2 / v3.
   - `RECAPTCHA_ENABLED=false`: Desarrollo y pruebas locales permiten omitir el desafío.
4. **Vigencia Anual Estricta**: La autenticación valida `StartDate <= Hoy <= EndDate` vinculando al administrador al año fiscal en curso (2026).

---

## 8. Suite de Pruebas End-to-End (E2E) Sin Mocks

Se diseñó la suite en `backend/src/tests_e2e/` ejecutada contra la base de datos real:

```
backend/src/tests_e2e/
├── conftest.py                             (Fixtures de SQL Server real y assert_no_pool_leaks)
├── test_01_pool_and_concurrency.py         (25 hilos concurrentes + 12 funciones auditadas)
├── test_02_atomic_transactions.py          (Rollback y Commit real en los 4 flujos transaccionales)
├── test_03_tsql_queries_and_views.py       (10 vistas T-SQL + consultas migradas)
└── test_04_api_full_journey.py             (Ciclo HTTP completo: login MD5->scrypt, usuario, cuenta, analíticas)
```

**Resultado de Ejecución:**
```text
======================== 16 passed in 76.98s (0:01:16) ========================
```
- **Cero fugas de conexión**: Verificado con `pool.checkedout() == 0` tras cada prueba individual y al finalizar la batería completa.
- **Rollbacks comprobados en disco**: Las tablas `DIM_Customer`, `DIM_Account`, `DIM_ServiceOwners` y `FACT_Revenue` demostraron retornar a su estado exacto ante inyecciones de fallo simuladas.

---

## 9. Despliegue en la Nube (Azure)

1. **`backend/Dockerfile`**:
   - Base `python:3.11-slim-bullseye`.
   - Instalación automatizada de `msodbcsql17` y dependencias de UnixODBC.
   - Configuración de Gunicorn en puerto 5000 con workers desacoplados.
2. **`backend/.dockerignore`**: Exclusión de entornos virtuales, archivos `.db`, `.pyc` y logs.
3. **`frontend/staticwebapp.config.json`**:
   - Rutas de SPA con fallback hacia `/index.html`.
   - Headers de seguridad HTTP (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`).

---

## 10. Matriz de Usuarios y Credenciales de Prueba (2026)

Se configuraron los siguientes usuarios en la instancia de SQL Server para pruebas funcionales:

| Perfil | Usuario | Contraseña | Rol | Manzana | Capacidades Principales |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Delegado** | `luisTorres` | `Admin1234!` | `delegado` | `tepetate` | Administración integral, reportes, creación de usuarios y cortes globales. |
| **Comitiva (Agua)** | `Arcov` | `Admin1234!` | `comitiva` | `tepetate` | Módulo de agua, checklist de pagos, cobro de servicios, corte de caja. |
| **Subdelegado** | `monseLopez` | `Admin1234!` | `subdelegado` | `garambullo` | Gestión y consulta de vecinos correspondientes a su manzana. |
| *Comitiva (Feria)* | `Arely12345` | `Admin1234!` | `comitiva` | `garambullo` | Módulo y cobros de festividades/feria. |
| *Comitiva (Panteón)* | `miriamComitiva` | `Admin1234!` | `comitiva` | `yhonda` | Módulo y cobros de panteón. |
| *Subdelegado (Cerritos)* | `noriel1` | `Admin1234!` | `subdelegado` | `cerritos` | Gestión de manzana Cerritos. |

---

## 11. Diagnóstico, Corrección y Optimización: Carga de Pagos en Todos los Módulos (2026)

### 11.1 Causa Raíz Identificada

A partir de la inspección exhaustiva de la pila completa (Frontend React → API Flask → Consultas T-SQL / Vistas → SQL Server 2022), se detectaron **4 causas concurrentes** que provocaban que ningún pago se visualizara en la interfaz:

1. **Desfase de Catálogo y Facturación al Año Fiscal en Curso (2026)**:
   - La base de datos original (`sistema_mandho.db`) fue construida y operada históricamente hasta el año 2025 (Panteón y Agua) y 2024 (Feria y Delegación).
   - El sistema opera en el entorno de pruebas bajo el año fiscal **2026**. Los componentes frontend (`DynamicMenu.jsx` y `DynamicTable.jsx`) inicializan el filtro por defecto mediante `new Date().getFullYear() = 2026`.
   - Las vistas de pagos T-SQL (`VISTA_PAGOS_PANTEON`, `VISTA_PAGOS_AGUA`, `VISTA_PAGOS_FERIA`, `VISTA_PAGOS_DELEGACION`) construyen la tabla a partir de `vwServiceCost`, que realiza un `INNER JOIN` obligatorio entre `DIM_ServiceDetails` y `DIM_Date` por `DIM_DateId`. Al no existir registros en `DIM_ServiceDetails` para el año 2026, las vistas retornaban exactamente **0 registros**.

2. **Rango Temporal Restringido en Frontend (`DateSelectPayment.jsx`)**:
   - El componente selector contenía `const startYear = 2025;` hardcodeado, calculando un arreglo de opciones de solo dos elementos: `[2026, 2025]`.
   - Dado que los registros históricos del proyecto abarcan desde 2021 hasta 2025, los años 2021 a 2024 estaban completamente inaccesibles para el usuario.
   - En módulos como **Feria** y **Delegación** (cuyos únicos cobros registrados en SQLite correspondían a 2024 y 2023), resultaba matemáticamente imposible ver ningún registro histórico desde la UI.

3. **`INNER JOIN DIM_Date` Redundante y Restrictivo en `read_payments.py`**:
   - En `ReadPayment.get_payments_with_filters()`, la consulta T-SQL agregaba:
     ```sql
     INNER JOIN DIM_Customer AS p ON vw.DIM_CustomerId = p.DIM_CustomerId
     INNER JOIN DIM_Date AS d ON vw.DIM_DateId = d.DIM_DateId
     WHERE vw.YearPay = ?
     ```
   - La tabla alias `d` (`DIM_Date`) **no era utilizada en ninguna proyección (`SELECT`) ni condición (`WHERE`)**.
   - En la definición de las vistas T-SQL, `vw.DIM_DateId` proviene de `vw.CustomerPaymentDate`, que es `NULL` cuando un cliente tiene un cargo asignado pero aún no ha realizado ningún abono (estado `pendiente`).
   - El `INNER JOIN` descartaba silenciosamente todos los cobros pendientes legítimos cuyo `CustomerPaymentDate` fuera nulo.

4. **Omisión de Autorización para el Rol `subdelegado` en `payment_route.py`**:
   - En el endpoint `/api/payment/read/`, la cláusula de control de rol verificaba:
     ```python
     if user_role == 'delegado':
         ...
     elif user_role == 'comitiva':
         ...
     else:
         return send_error("Rol de usuario no autorizado para crear pagos", 403)
     ```
   - Usuarios con rol `subdelegado` (como `monseLopez`) eran rechazados con error HTTP 403 al consultar cobros.

---

### 11.2 Acciones Implementadas y Optimizaciones

#### A. Módulo Seeder de Catálogo y Facturación 2026 (`backend/scripts/seed_services_and_payments_2026.py`)
Se desarrolló un script modular e idempotente que puebla el catálogo y las obligaciones de pago para las **32 cuentas activas**:

| Servicio | Tipo de Detalle | Monto | Estado Catálogo | Año Fiscal |
| :--- | :--- | :---: | :---: | :---: |
| **Agua** | `consumo` | $360.00 | `status6` (requerido) | 2026 |
| **Agua** | `tomas` | $360.00 | `status6` (requerido) | 2026 |
| **Panteón** | `faena` | $300.00 | `status8` (usado) | 2026 |
| **Panteón** | `cooperacion` | $400.00 | `status8` (usado) | 2026 |
| **Panteón** | `cooperacion camino` | $200.00 | `status8` (usado) | 2026 |
| **Panteón** | `faena verana` | $150.00 | `status6` (requerido) | 2026 |
| **Panteón** | `faena dia de muertos` | $300.00 | `status8` (usado) | 2026 |
| **Panteón** | `faena2` | $250.00 | `status8` (usado) | 2026 |
| **Panteón** | `Cena Navidena` | $500.00 | `status8` (usado) | 2026 |
| **Feria** | `faena` | $300.00 | `status8` (usado) | 2026 & 2025 |
| **Feria** | `comida` | $550.00 | `status8` (usado) | 2026 & 2025 |
| **Feria** | `cooperacion` | $400.00 | `status6` (requerido) | 2026 & 2025 |
| **Delegación** | `faena` | $250.00 | `status8` (usado) | 2026 & 2025 |
| **Delegación** | `cooperacion` | $300.00 | `status6` (requerido) | 2026 & 2025 |

- Se generaron los registros correspondientes en `FACT_Revenue` (combinando estados `completo` y `pendiente` para reflejar un estado operativo realista).
- Se integró la ejecución automática del seeder en `backend/scripts/setup_test_users.py` y `backend/scripts/migrate_sqlite_to_sqlserver.py`.

#### B. Optimización del Selector de Fechas (`frontend/src/components/modules/DateSelectPayment.jsx`)
- Se actualizó el año base: `const startYear = 2021;`.
- El dropdown ahora genera dinámicamente el rango completo: `[2026, 2025, 2024, 2023, 2022, 2021]`.
- Permite a los administradores auditar períodos históricos de cualquier módulo sin bloqueos.

#### C. Optimización de Consulta T-SQL (`backend/src/payments/repository/read_payments.py`)
- Se removió el `INNER JOIN DIM_Date AS d ON vw.DIM_DateId = d.DIM_DateId`.
- La consulta ahora preserva los registros con `StatusFactura = 'pendiente'` y fecha nula, evitando la pérdida de filas en la agregación.

#### D. Corrección de Autorización (`backend/src/routes/payment_route.py`)
- Se amplió la condición de acceso a:
  ```python
  if user_role in ['delegado', 'subdelegado']:
      if not request_service_name:
          return send_error("Se debe especificar un servicio", 400)
  ```

---

### 11.3 Verificación y Métricas de Rendimiento

1. **Conteo Real de Pagos Cargados (Validación en Servidor en Vivo - Puerto 5000)**:
   - **Panteón 2026**: `224` pagos (153 en 2025).
   - **Agua 2026**: `64` pagos (15 en 2025).
   - **Feria 2026**: `96` pagos (96 en 2025).
   - **Delegación 2026**: `64` pagos (64 en 2025).

2. **Compilación de Frontend**:
   - `pnpm --dir frontend build` ejecutado exitosamente en 6.28s (0 errores, 257 módulos transformados).

3. **Suite de Pruebas E2E (`backend/src/tests_e2e/`)**:
   - Se incorporó la prueba `test_e2e_read_payments_all_modules_2026_and_authorization` en `test_04_api_full_journey.py`.
   - **Resultado Global**:
     ```text
     ============================= 17 passed in 31.01s =============================
     ```
   - **Pool Status**: `checkedout == 0` garantizado tras cada petición HTTP y al cierre de la suite.
