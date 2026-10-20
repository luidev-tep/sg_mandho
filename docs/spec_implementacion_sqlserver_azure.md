# Especificaciones Técnicas de Implementación (SPECs) — S.G. El Mandhó

> [!IMPORTANT]
> **Alcance del documento**: Especificación técnica exhaustiva y accionable para que el modelo ejecutor implemente de principio a fin la migración de SQLite a SQL Server (Local + Azure SQL Serverless), el rediseño del pool de conexiones (`QueuePool`), las transacciones atómicas (`shared_conn`), el cierre de las 12 fugas de conexión y la **Suite de Tests End-to-End (E2E) sin mocks contra SQL Server real**.

---

## 1. Registro de Estado: Hechos, Decisiones, Hipótesis y Pendientes

### 1.1 Hechos Verificados (`HECHO VERIFICADO`)
1. **Discrepancias Críticas entre `.db` vivo (`backend/database/sistema_mandho.db`) y `backend/Data_Base_Schema.sql`**:
   - **Vistas**: El `.db` vivo tiene **10 vistas** (`SecurityUsers`, `VISTA_CLIENTES_ACTIVOS`, 4 `VISTA_PAGOS_*`, 4 `VISTA_PAGOS_DETALLADO_*`). El SQL del repo solo tiene 3.
   - **Columna faltante en DDL**: `DIM_ServiceDetails` en el `.db` vivo tiene la columna `DIM_StatusId TEXT` con FK a `DIM_Status(DIM_StatusId)`. No existe en `Data_Base_Schema.sql`, pero el código Python la inserta y consulta en `src/dim_servicedetails/repository/create.py`, `src/dim_servicedetails/repository/update.py`, `src/payments/repository/cash_cut_querys.py` y `src/payments/repository/get_check_list.py`.
   - **Registros de catálogo faltantes en seeds**: `DIM_Status` en el `.db` vivo tiene **8 registros**, mientras que `Data_Base_Schema.sql` e `initial_information.sql` solo insertan 5 (`status1` a `status5`). Los 3 faltantes son indispensables para crear servicios, checklists y cortes de caja:
     - `('status6', 'requerido')`
     - `('status7', 'nousado')`
     - `('status8', 'usado')`
   - **Calendario `DIM_Date` vencido en `.db` vivo**: `SELECT MIN(Year), MAX(Year), COUNT(*) FROM DIM_Date` en el `.db` vivo devuelve `(2021, 2025, 1825)`. **No existen fechas para 2026 en adelante**. Dado que `DIM_DATE.__init__()` busca la fecha actual (`America/Mexico_City`) en `DIM_Date` en cada operación, si `2026` no está poblado, `self.dateId` vale `None` y **todas las inserciones con FK a `DIM_DateId` (`NOT NULL`) fallan en 2026**.
   - **Error de sintaxis FK**: En `DIM_CashCut` (`Data_Base_Schema.sql:145-146`) falta una coma entre las dos últimas definiciones `FOREIGN KEY`.
2. **Acoplamiento y Fugas de Conexión (Connection Leaks) en la base de código**:
   - 31 archivos consumen `Conexion` (`src/utils/conexion.py`); 23 archivos importan `sqlite3`.
   - Existen **12 funciones en 9 archivos** donde la conexión no se cierra o no tiene bloque `finally`, lo que en un `QueuePool(pool_size=5, max_overflow=10)` agotaría todas las conexiones en 15 peticiones y colgaría el servidor con `TimeoutError`.
3. **Bug latente en `DIM_ServiceOnwers` (`src/dim_serviceonwers/repository/show.py:16`)**:
   - La consulta ejecuta `SELECT DIM_ServiceOnwersId FROM DIM_ServiceOnwers`, pero la tabla real en la BD se llama `DIM_ServiceOwners` (con `wn`, no `nw`).
4. **Bug latente en `PaymentProcesor.py` (`src/analytics_reports/repository/PaymentProcesor.py:56`)**:
   - Ejecuta `strftime(Year) as year` con un solo argumento, lo que en SQLite retorna `NULL` y en T-SQL lanza error de función inexistente.
5. **Transacciones rotas en flujos multi-paso**:
   - **Flujo 1 (`insert_new_Onwer`)**: Ejecuta hasta 4 escrituras en conexiones independientes (`descativar_otra_cuenta`, `insert` en `DIM_Account`, `update_user_info` en `DIM_Customer`, `insert_service_owner_info` en `DIM_ServiceOwners`).
   - **Flujo 2 (`CashCut`)**: Ejecuta `insert_many_fact_revenues` y luego `create_cash_cut_register` en conexiones separadas.
   - **Flujo 3 (`insert_many_register` — Pagos por Checklist)**: En `src/fact_revenues/Fact_revenue.py:167-174` inserta masivamente en `FACT_Revenue` y luego actualiza `DIM_ServiceDetails` a `'status8'` en otra conexión.
6. **Codificación de `requirements.txt`**: `backend/requirements.txt` está en `UTF-16LE`.

### 1.2 Decisiones Tomadas (`DECISIÓN TOMADA`)
1. **Motor y Driver**: SQL Server con `pyodbc` + `ODBC Driver 18 for SQL Server` y pool `QueuePool` de `SQLAlchemy`.
2. **Alcance del Pool y Refactorización**: Implementar **Fase 1 + Fase 2 completa** (Pool + cierre de todas las fugas + soporte de transacciones atómicas sin mocks en los flujos multi-paso).
3. **Tipos de Datos Conservadores en T-SQL**: Mantener fechas de negocio como `NVARCHAR(20)` (preservando `'YYYY-MM-DD'` y `'s/n'`) y montos como `FLOAT` para no romper la serialización JSON ni comparaciones en Python.
4. **Testing E2E Real (Cero Mocks de BD)**: Construir una suite de pruebas End-to-End (`backend/src/test/test_e2e_sqlserver/`) que se conecte directamente a la instancia local de SQL Server, pruebe el pool bajo concurrencia, verifique `commit` y `rollback` reales en BD ante fallos intermedios, y ejecute todos los endpoints de Flask con `app.test_client()` contra datos reales.
5. **Entorno Local y Azure**: Instancia local de SQL Server para desarrollo/tests; en Azure: Container Apps (Consumption) + Static Web Apps (Free) + Azure SQL Serverless (Free Tier, todo público).
6. **Fase 0 obligatoria**: Cerrar verificación y commit de seguridad antes de iniciar la refactorización de BD.

---

## 2. SPEC-01: Cierre de Correcciones de Seguridad y Limpieza (Fase 0)

### 2.1 Verificaciones y Ajustes Previos al Commit
1. **`backend/.env`**: Añadir `http://localhost:5173` a `URL_FRONTEND` separado por coma.
2. **Validación de Hashing en Python**: Verificar con pytest que `SecurityUsers` valide contraseñas contra hashes `MD5` legados (32 hex) usando `hmac.compare_digest` y contra hashes `scrypt:...` generados por Werkzeug.
3. **Ejecución de Línea Base**:
   - Backend: `.\backend\venv\Scripts\python.exe -m pytest backend/src/test -q` (comparar contra 20F/26P).
   - Frontend: `pnpm --dir frontend build` (debe compilar con código 0).
4. **Actualización de `backend/README.md` y `frontend/README.md`**:
   - Actualizar estado de hashing (`Werkzeug scrypt` + migración en login), `reCAPTCHA v2` activo por defecto, unificación de `axiosInstance.js`, eliminación de `Lista.jsx` y `react-toast`, corrección de `favicon.png`, y documentar explícitamente la preservación de erratas (`Singup.jsx`, `gat_data`, `ServiceDetailesType`, `DIM_ServiceOnwers`) y lecturas vía `POST`.
5. **Commit de Fase 0**: Hacer commit de todos los cambios de seguridad, limpieza y documentación antes de tocar código de SQL Server.

---

## 3. SPEC-02: Diseño Profundo del Núcleo `Conexion`, Pool y Transacciones (Fases 1 y 2)

Esta es la pieza más sensible de la arquitectura. Debe permitir que los **31 archivos existentes** sigan funcionando sin cambiar su estructura de llamadas, al tiempo que previene fugas de conexiones y habilita transacciones atómicas reales (`BEGIN` / `COMMIT` / `ROLLBACK`) cuando varias funciones de repositorio participan en una misma operación.

### 3.1 Diseño Exacto de `backend/src/utils/conexion.py`

```python
import os
import urllib.parse
from typing import Optional, Tuple, Any
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

load_dotenv()

_engine: Optional[Engine] = None


def _build_odbc_connection_string() -> str:
    driver = os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    server = os.environ.get("DB_SERVER", "localhost,1433")
    database = os.environ.get("DB_NAME", "sg_mandho")
    user = os.environ.get("DB_USER", "sa")
    password = os.environ.get("DB_PASSWORD", "")
    encrypt = os.environ.get("DB_ENCRYPT", "yes")
    trust_cert = os.environ.get("DB_TRUST_CERT", "yes")
    timeout = os.environ.get("DB_CONNECT_TIMEOUT", "30")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust_cert};"
        f"Connection Timeout={timeout};"
        "ConnectRetryCount=3;"
        "ConnectRetryInterval=10;"
    )


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        conn_str = _build_odbc_connection_string()
        odbc_url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str)
        _engine = create_engine(
            odbc_url,
            poolclass=QueuePool,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            pool_pre_ping=True,
            pool_recycle=1800,
            # Desactivar autocommit en pyodbc para garantizar control transaccional explícito
            connect_args={"autocommit": False},
        )
    return _engine


def get_pool_status() -> dict[str, int]:
    """Utilidad de diagnóstico y para assertions en tests E2E de fugas de conexión."""
    engine = _get_engine()
    pool = engine.pool
    return {
        "size": pool.size(),
        "checkedin": pool.checkedin(),
        "checkedout": pool.checkedout(),
        "overflow": pool.overflow(),
    }


def dispose_engine() -> None:
    """Cierra todas las conexiones físicas del pool (útil en teardown de tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


class Conexion:
    """
    Gestiona una conexión a SQL Server obtenida del QueuePool de SQLAlchemy.
    
    Modos de uso:
    1. Autónomo (por defecto, compatible con los 31 módulos):
       db = Conexion()
       db.cursor.execute(...)
       db.save_changes()
       db.close_conexion()
       
    2. Transacción compartida (Unidad de Trabajo / Fase 2):
       with Conexion() as tx:
           repo_step_1(data, db=tx)  # internamente hace Conexion(shared_conn=tx)
           repo_step_2(data, db=tx)
           tx.save_changes()         # único commit al final
    """

    def __init__(self, shared_conn: Optional["Conexion"] = None) -> None:
        self._closed = False
        if shared_conn is not None:
            # Modo préstamo: participa en la transacción de shared_conn
            self._owns_connection = False
            self.conn = shared_conn.conn
            self.cursor = shared_conn.cursor
            self.__ruta = shared_conn.get_route()
        else:
            # Modo autónomo: toma una conexión del pool
            self._owns_connection = True
            server = os.environ.get("DB_SERVER", "localhost,1433")
            database = os.environ.get("DB_NAME", "sg_mandho")
            self.__ruta = f"{server}/{database}"
            try:
                self.conn = _get_engine().raw_connection()
                self.cursor = self.conn.cursor()
            except pyodbc.Error as e:
                print(f"Error al conectar con la base de datos SQL Server: {e}")
                raise

    def get_route(self) -> str:
        return self.__ruta

    def conexion(self) -> Tuple[Any, Any]:
        if self.conn is None or self.cursor is None:
            raise pyodbc.Error("La conexión o el cursor no están inicializados.")
        return self.conn, self.cursor

    def save_changes(self) -> None:
        """
        Hace commit de la transacción actual SOLO si esta instancia es dueña de la conexión.
        Si es una conexión prestada (_owns_connection=False), delega el commit al coordinador.
        """
        if not self._owns_connection:
            return
        try:
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Error al guardar los cambios (commit): {e}")
            raise

    def rollback(self) -> None:
        """Revierte explícitamente los cambios no confirmados en la conexión actual."""
        try:
            if self.conn:
                self.conn.rollback()
        except pyodbc.Error as e:
            print(f"Error al revertir los cambios (rollback): {e}")
            raise

    def close_conexion(self) -> None:
        """
        Devuelve la conexión al QueuePool si esta instancia es la dueña.
        Idempotente: llamar a close_conexion() dos veces no lanza error.
        """
        if not self._owns_connection or self._closed:
            return
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.conn is not None:
                # SQLAlchemy _ConnectionFairy ejecuta rollback() automático de cambios
                # no commiteados antes de devolver la conexión al QueuePool.
                self.conn.close()
            self._closed = True
        except pyodbc.Error as e:
            print(f"Error al devolver la conexión al pool: {e}")
            raise

    def __enter__(self) -> "Conexion":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._owns_connection:
            if exc_type is not None:
                try:
                    self.conn.rollback()
                except Exception:
                    pass
            self.close_conexion()
        return False
```

---

### 3.2 Mapa Exhaustivo de Cierre de Fugas de Conexión (12 Puntos en 9 Archivos)

Cada uno de los siguientes 12 puntos **debe** corregirse en la Fase 1/2:

| # | Archivo | Función y Líneas | Bug Actual Verificado | Corrección Exacta Especificada |
|---|---|---|---|---|
| 1 | `src/routes/search_real_time.py` | `busqueda_tiempo_real()` L106-185 | Inicializa `db_handler = Conexion()` pero en `finally` hace `if conn: conn.close()`, dejando `db_handler.cursor` abierto y rompiendo la abstracción. | Inicializar `db_handler = None` antes del `try`, y en `finally:` llamar a `if db_handler: db_handler.close_conexion()`. |
| 2 | `src/analytics_reports/repository/PaymentProcesor.py` | `get_all_data_payments()` L37-110 | Abre `handler_conexion = Conexion()` en L37 y **jamás la cierra** en ningún camino. | Envolver todo el bloque L71-110 en `try: ... finally: handler_conexion.close_conexion()`. |
| 3 | `src/accounts/services/validate.py` | `validate_account()` L33-49 | Abre `object_connection = Conexion()` en L33 y **jamás la cierra**. Además usa f-string SQL `WHERE DIM_CustomerId = '{user_id}'` (riesgo de inyección). | Envolver en `try: ... finally: object_connection.close_conexion()` y parametrizar con `WHERE DIM_CustomerId = ? AND DIM_StatusId = 'status1'`, `(user_id,)`. |
| 4 | `src/accounts/services/validate.py` | `has_active_account()` L160-178 | Abre `object_connection = Conexion()` en L175 y **jamás la cierra**. | Envolver L176-178 en `try: ... finally: object_connection.close_conexion()`. |
| 5 | `src/payments/services/validate_payment.py` | `is_account_active()` L73-94 | Abre `handler_coneccion = Conexion()` en L80 y **jamás la cierra**. | Envolver L87-94 en `try: ... finally: handler_coneccion.close_conexion()`. |
| 6 | `src/payments/repository/read_payments.py` | `get_validation_payment()` L246-277 | En `finally:` (L276) tiene comentado `# hanlder_conexion.close_conexion()` bajo la creencia errónea de que la conexión se reutilizaba afuera. | Descomentar `hanlder_conexion.close_conexion()` en el bloque `finally`. |
| 7 | `src/dim_serviceonwers/repository/show.py` | `get_ServiceOnwers_by_name()` L4-26 | Abre `object_conecction = Conexion()` en L14 y **jamás la cierra**. Además consulta la tabla mal escrita `DIM_ServiceOnwers`. | Añadir `finally: object_conecction.close_conexion()` y corregir la consulta a `SELECT DIM_ServiceOwnersId FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?`. |
| 8 | `src/dim_dates/dim_date.py` | `get_by_id()` L39-62 | Abre `connection = Conexion()` dentro del `try` (L50) y **jamás la cierra**. | Instanciar `connection = Conexion()` antes del `try` y añadir `finally: connection.close_conexion()`. |
| 9 | `src/users/repository/show.py` | `get_all_users()` L9-43 | Abre `handlers = Conexion()` en L17 y **jamás la cierra**. | Envolver L18-43 en `try: ... finally: handlers.close_conexion()`. |
| 10 | `src/users/repository/show.py` | `get_users_with_filters()` L101-183 | Abre `conecion = Conexion()` en L114 y **jamás la cierra** ni en éxito ni en excepción. | Añadir bloque `finally: conecion.close_conexion()`. |
| 11 | `src/accounts/repository/show.py` | `show_account()` L5-49 | Llama a `conecion.close_conexion()` después de `fetchall()`, pero sin `try/finally` (si `execute` lanza excepción, la conexión queda huérfana). | Envolver en `try: ... finally: conecion.close_conexion()`. |
| 12 | `src/users/repository/create.py`, `src/accounts/repository/insert.py`, `src/dim_roles/repository/create.py`, `src/dim_roles/repository/show.py` | `insert_user`, `insert`, `insertar_role`, `get_role` | Cierran manualmente en `try` y en `except sqlite3.Error`, pero si ocurre cualquier otra excepción no hay `finally`. En `insertar_role` además se usa f-string SQL. | Estandarizar todos a `conn = Conexion(shared_conn=db)` fuera del `try` y `finally: conn.close_conexion()`. Parametrizar `WHERE RoleName = ?` en `insertar_role`. |

---

### 3.3 Especificación de los 3 Flujos Transaccionales Atómicos (Fase 2)

#### Flujo Transaccional A: Creación de Administrador (`insert_new_Onwer` → `insert_onwer_info`)
- **Cambios de firma requeridos**:
  - `src/accounts/services/validate.py`: `def descativar_otra_cuenta(Customer_id: str, db: Conexion | None = None) -> None:` usa `handler_conn = Conexion(shared_conn=db)` y relanza `pyodbc.Error` si `db is not None`.
  - `src/accounts/account.py`: `def insert_account(self, account_json: dict, db: Conexion | None = None) -> tuple:` y `def desactivate_account(self, persona_id: str, db: Conexion | None = None) -> None:` propagan `db` a `descativar_otra_cuenta` e `insert(cuenta, db=db)`.
  - `src/accounts/repository/insert.py`: `def insert(data: object, db: Conexion | None = None) -> tuple[bool, str]:` usa `object_conecction = Conexion(shared_conn=db)`.
  - `src/security/repository/user_info.py`: `def update_user_info(password: str, username: str, dim_customer_id: str, db: Conexion | None = None) -> tuple[int, str]:` usa `handler_connection = Conexion(shared_conn=db)`.
  - `src/security/repository/user_info.py`: `def insert_service_owner_info(data: dict, db: Conexion | None = None) -> bool:` usa `handler_connection = Conexion(shared_conn=db)`.
  - `src/security/repository/user_info.py`: `insert_onwer_info(data: dict)` coordina todo con `with Conexion() as tx:`:
    ```python
    with Conexion() as tx:
        estado, mensaje = handler_account.insert_account(data_for_account, db=tx)
        if estado != 200:
            tx.rollback()
            return estado, mensaje

        estado, mensaje = update_user_info(data['password'], data['username'], data['DIM_CustomerId'], db=tx)
        if estado != 200:
            tx.rollback()
            return estado, mensaje

        if not insert_service_owner_info(data_service_owner, db=tx):
            tx.rollback()
            return 500, "No se pudo insertar el nuevo usuario"

        tx.save_changes()
        return 200, "Usuario insertado correctamente"
    ```

#### Flujo Transaccional B: Corte de Caja (`cashCutCrud.CashCut`)
- **Cambios de firma requeridos**:
  - `src/fact_revenues/repository/insert.py`: `def insert_many_fact_revenues(data_revenue: list[FACT_Revenue], db: Conexion | None = None) -> bool:` usa `object_conetion = Conexion(shared_conn=db)` y `object_conetion.cursor.fast_executemany = True`.
  - `src/payments/repository/cash_cut_querys.py`: `def create_cash_cut_register(data_json: CashCutModel, db: Conexion | None = None) -> bool:` usa `handler = Conexion(shared_conn=db)`.
  - `src/payments/cash_cut.py`: Envolver ambos pasos en `with Conexion() as tx:`; si cualquiera falla, ejecutar `tx.rollback()` y retornar `500`; si ambos pasan, ejecutar `tx.save_changes()`.

#### Flujo Transaccional C: Pagos Masivos por Checklist (`factRevenueCrud.insert_many_register`)
- **Cambios de firma requeridos**:
  - `src/dim_servicedetails/repository/update.py`: `def update_ServiceDetails(status_id: str, DIM_ServiceDetailsId: str, db: Conexion | None = None) -> bool:` usa `object_conetion = Conexion(shared_conn=db)`.
  - `src/dim_servicedetails/serviceDetails.py`: `Update_dim_service_details(..., db: Conexion | None = None)`.
  - `src/fact_revenues/Fact_revenue.py`: Ejecutar `insert_many_fact_revenues(model_format, db=tx)` y `Update_dim_service_details(..., db=tx)` dentro de `with Conexion() as tx:`.

---

## 4. SPEC-03: Inventario Completo de Cambios por Archivo en el Backend

### 4.1 Tabla Maestra de los 23 Archivos con `sqlite3` y Consultas con Dialecto SQLite

| # | Archivo | Cambio de Excepción/Import | Cambio de Consulta SQL / Lógica de Conexión |
|---|---|---|---|
| 1 | `src/utils/conexion.py` | `sqlite3` → `pyodbc`, `SQLAlchemy QueuePool` | Reescritura completa según SPEC-02 (§3.1). Elimina `PRAGMA journal_mode=WAL` y `PRAGMA busy_timeout`. |
| 2 | `src/accounts/services/validate.py` | `sqlite3.Error` → `pyodbc.Error` | Cerrar fugas en `validate_account` y `has_active_account`. Parametrizar query en L35. Soportar `db=None` en `descativar_otra_cuenta`. |
| 3 | `src/dim_dates/dim_date.py` | `sqlite3.Error` → `pyodbc.Error` | Cerrar fuga en `get_by_id` (L50). En `_insert_year_dates` (L156): cambiar `INSERT OR IGNORE INTO DIM_Date` por consulta previa de `DIM_DateId` existentes o `MERGE`, ya que T-SQL no soporta `INSERT OR IGNORE`. |
| 4 | `src/dim_roles/repository/show.py` | `sqlite3.Error` → `pyodbc.Error` | Mover `object_connection.close_conexion()` a bloque `finally`. |
| 5 | `src/dim_servicedetails/repository/create.py` | `sqlite3.Error` → `pyodbc.Error` | Sin cambio de SQL (ya usa `?` e incluye `DIM_StatusId`). |
| 6 | `src/dim_servicedetails/repository/show.py` | Eliminar `import sqlite3` (no usado) o cambiar a `pyodbc` | Sin cambio de SQL (6 funciones ya usan `finally: close_conexion()`). |
| 7 | `src/dim_servicedetails/repository/update.py` | `sqlite3.Error` → `pyodbc.Error` | Añadir `db: Conexion | None = None` para participar en Flujo Transaccional C. |
| 8 | `src/dim_serviceonwers/repository/show.py` | `sqlite3.Error` → `pyodbc.Error` | Corregir nombre de tabla/columna en L16: `SELECT DIM_ServiceOwnersId FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?` y añadir `finally: object_conecction.close_conexion()`. |
| 9 | `src/dim_status/status.py` | `sqlite3.Error` → `pyodbc.Error` | Sin cambio de SQL (ambos métodos tienen `finally: self.conexion.close_conexion()`). |
| 10 | `src/fact_revenues/repository/edit.py` | `sqlite3.Error` → `pyodbc.Error` | En `update_many_registers`: validar que `data_ids` no sea lista vacía antes de armar `IN ()` (evita error de sintaxis `IN ()` en SQL Server). |
| 11 | `src/fact_revenues/repository/insert.py` | `sqlite3.Error` → `pyodbc.Error` | Añadir `db: Conexion | None = None` y `object_conetion.cursor.fast_executemany = True` en `insert_many_fact_revenues`. |
| 12 | `src/payments/repository/cash_cut_querys.py` | `sqlite3.Error` → `pyodbc.Error` | Añadir `db: Conexion | None = None` en `create_cash_cut_register` para el Flujo Transaccional B. |
| 13 | `src/payments/repository/get_fact_revenues_customer.py` | `sqlite3.Error` → `pyodbc.Error` | Sin cambio de SQL (consulta `VISTA_PAGOS_DETALLADO_*` con `?`). |
| 14 | `src/payments/repository/get_pending_pays.py` | `sqlite3.Error` → `pyodbc.Error` | Sin cambio de SQL (CTEs estándar compatibles con T-SQL). |
| 15 | `src/payments/repository/read_payments.py` | `sqlite3.Error` → `pyodbc.Error` | Descomentar `hanlder_conexion.close_conexion()` en L276 (`get_validation_payment`). |
| 16 | `src/payments/services/validate_payment.py` | `sqlite3.Error` → `pyodbc.Error` | Añadir `try ... finally: handler_coneccion.close_conexion()` en `is_account_active` (L80). |
| 17 | `src/security/repository/get_onwers_info.py` | `sqlite3.Error` → `pyodbc.Error` | En `get_securyty_users_info()` (L41): añadir `ORDER BY StartDate DESC` a `SELECT * FROM SecurityUsers ORDER BY StartDate DESC` (ya que se retira el `ORDER BY` de la definición de la vista en T-SQL). |
| 18 | `src/security/repository/user_info.py` | `sqlite3.Error` → `pyodbc.Error` | Implementar `with Conexion() as tx:` en `insert_onwer_info` y parámetro `db=None` en `update_user_info` e `insert_service_owner_info`. |
| 19 | `src/users/repository/create.py` | `sqlite3.Error` → `pyodbc.Error` | En L60: cambiar `str(data.DIM_DateId)` por `int(data.DIM_DateId)` (la columna `DIM_DateId` es `INT`) y mover `close_conexion()` a `finally`. |
| 20 | `src/users/repository/delete.py` | `sqlite3.Error` → `pyodbc.Error` | En `defuncion_validation` (L45): cambiar `if result[0] == "s/n" or result is None:` por `if result is None or result[0] == "s/n":` (evita `TypeError` si el usuario no existe). |
| 21 | `src/users/repository/edit.py` | `sqlite3.Error` → `pyodbc.Error` | Sin cambio de SQL. |
| 22 | `src/users/repository/home_info.py` | `sqlite3.Error` → `pyodbc.Error` | En L18: cambiar `cu.CustomerFraction \|\| ' ' \|\| cu.CustomerAddress \|\| ' ' \|\| cu.CustomerNumberExt AS adress` por `CONCAT(cu.CustomerFraction, ' ', cu.CustomerAddress, ' ', cu.CustomerNumberExt) AS adress`. |
| 23 | `src/users/repository/show.py` | `sqlite3.Error` → `pyodbc.Error` | En L147: cambiar `AND p.CustomerEndDate is not 's/n'` por `AND p.CustomerEndDate <> 's/n'`. Añadir `finally: close_conexion()` en `get_all_users`, `get_user` y `get_users_with_filters`. |

### 4.2 Archivos Adicionales sin `import sqlite3` pero con SQL o Fugas a Corregir
| # | Archivo | Cambio Especificado |
|---|---|---|
| 24 | `src/routes/search_real_time.py` | Cambiar `SELECT ... FROM DIM_Customer WHERE ... LIMIT 50` por `SELECT TOP 50 ... FROM DIM_Customer WHERE ...`. Corregir cierre en `finally` a `db_handler.close_conexion()`. |
| 25 | `src/analytics_reports/repository/get_analytics.py` | En L185: cambiar `IFNULL(SUM(vw.amount), 0) as revenue` por `ISNULL(SUM(vw.amount), 0) as revenue`. |
| 26 | `src/analytics_reports/repository/PaymentProcesor.py` | En L56: cambiar `strftime(Year) as year` por `CAST(d.Year AS NVARCHAR(10)) as Year`. Añadir `finally: handler_conexion.close_conexion()`. |
| 27 | `src/accounts/repository/insert.py` y `show.py` | Añadir bloque `finally: close_conexion()` y soporte `db=None` en `insert`. |
| 28 | `src/dim_roles/repository/create.py` | Parametrizar `WHERE RoleName = ?` y usar `finally: object_conecction.close_conexion()`. |

---

## 5. SPEC-04: DDL T-SQL Completo (`01_schema_tsql.sql`, `02_views_tsql.sql`, `03_seed_tsql.sql`)

### 5.1 Definición Exacta de las 11 Tablas (`backend/sql/01_schema_tsql.sql`)

```sql
-- =============================================================================
-- 01_schema_tsql.sql — Esquema T-SQL para SQL Server / Azure SQL Database
-- =============================================================================

DROP VIEW IF EXISTS VISTA_PAGOS_DETALLADO_PANTEON;
DROP VIEW IF EXISTS VISTA_PAGOS_DETALLADO_FERIA;
DROP VIEW IF EXISTS VISTA_PAGOS_DETALLADO_DELEGACION;
DROP VIEW IF EXISTS VISTA_PAGOS_DETALLADO_AGUA;
DROP VIEW IF EXISTS VISTA_PAGOS_PANTEON;
DROP VIEW IF EXISTS VISTA_PAGOS_FERIA;
DROP VIEW IF EXISTS VISTA_PAGOS_DELEGACION;
DROP VIEW IF EXISTS VISTA_PAGOS_AGUA;
DROP VIEW IF EXISTS VISTA_CLIENTES_ACTIVOS;
DROP VIEW IF EXISTS SecurityUsers;

DROP TABLE IF EXISTS DIM_CashCut;
DROP TABLE IF EXISTS FACT_Revenue;
DROP TABLE IF EXISTS DIM_ServiceOwners;
DROP TABLE IF EXISTS DIM_ServiceDetails;
DROP TABLE IF EXISTS DIM_Account;
DROP TABLE IF EXISTS DIM_Customer;
DROP TABLE IF EXISTS DIM_Movement;
DROP TABLE IF EXISTS DIM_Service;
DROP TABLE IF EXISTS DIM_Date;
DROP TABLE IF EXISTS DIM_Status;
DROP TABLE IF EXISTS DIM_Role;

CREATE TABLE DIM_Role (
    DIM_RoleId NVARCHAR(64) NOT NULL PRIMARY KEY,
    RoleName NVARCHAR(100) NOT NULL,
    RoleType NVARCHAR(50) NOT NULL,
    RoleStartDate NVARCHAR(20) NOT NULL,
    RoleEndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Status (
    DIM_StatusId NVARCHAR(64) NOT NULL PRIMARY KEY,
    StatusName NVARCHAR(100) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Date (
    DIM_DateId INT NOT NULL PRIMARY KEY,
    FiscalYear NVARCHAR(10) NOT NULL,
    FiscalMonth NVARCHAR(10) NOT NULL,
    FiscalQuarter NVARCHAR(10) NOT NULL,
    FiscalWeek NVARCHAR(10) NOT NULL,
    FiscalDay NVARCHAR(10) NOT NULL,
    [Year] INT NOT NULL,
    [Month] NVARCHAR(10) NOT NULL,
    [Week] NVARCHAR(10) NOT NULL,
    [Day] NVARCHAR(10) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Customer (
    DIM_CustomerId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    CustomerName NVARCHAR(100) NOT NULL,
    CustomerMiddleName NVARCHAR(100) DEFAULT N's/n',
    CustomerLastName NVARCHAR(100) NOT NULL,
    CustomerSecondLastName NVARCHAR(100) DEFAULT N's/n',
    CustomerDateBirth NVARCHAR(20) NOT NULL,
    CustomerStartDate NVARCHAR(20) NOT NULL,
    CustomerEndDate NVARCHAR(20) DEFAULT N's/n',
    CustomerFraction NVARCHAR(100) DEFAULT N's/n',
    CustomerAddress NVARCHAR(255) DEFAULT N's/n',
    CustomerNumberExt NVARCHAR(50) DEFAULT N's/n',
    username NVARCHAR(100) DEFAULT N'n/a',
    [password] NVARCHAR(255) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_Customer_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId)
);

CREATE TABLE DIM_Account (
    DIM_AccountId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NOT NULL,
    DIM_CustomerId NVARCHAR(64) NOT NULL,
    DIM_RoleId NVARCHAR(64) NOT NULL,
    DIM_StatusId NVARCHAR(64) NOT NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_Account_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_Account_Customer FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId),
    CONSTRAINT FK_Account_Role FOREIGN KEY (DIM_RoleId) REFERENCES DIM_Role(DIM_RoleId),
    CONSTRAINT FK_Account_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_Service (
    DIM_ServiceId NVARCHAR(64) NOT NULL PRIMARY KEY,
    ServiceName NVARCHAR(100) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_ServiceDetails (
    DIM_ServiceDetailsId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_ServiceId NVARCHAR(64) NULL,
    ServiceDetailesType NVARCHAR(100) NULL,
    amount FLOAT NULL CHECK (amount >= 0.0),
    DIM_StatusId NVARCHAR(64) NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_ServiceDetails_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_ServiceDetails_Service FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId),
    CONSTRAINT FK_ServiceDetails_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_ServiceOwners (
    DIM_ServiceOwnersId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_ServiceId NVARCHAR(64) NULL,
    DIM_CustomerId NVARCHAR(64) NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_ServiceOwners_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_ServiceOwners_Service FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId),
    CONSTRAINT FK_ServiceOwners_Customer FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId)
);

CREATE TABLE DIM_Movement (
    DIM_MovementId NVARCHAR(64) NOT NULL PRIMARY KEY,
    MovementName NVARCHAR(100) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE FACT_Revenue (
    FACT_RevenueId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_AccountId NVARCHAR(64) NULL,
    DIM_ServiceDetailsId NVARCHAR(64) NULL,
    DIM_MovementId NVARCHAR(64) NULL,
    DIM_StatusId NVARCHAR(64) NULL,
    amount FLOAT NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_Revenue_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_Revenue_Account FOREIGN KEY (DIM_AccountId) REFERENCES DIM_Account(DIM_AccountId),
    CONSTRAINT FK_Revenue_ServiceDetails FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
    CONSTRAINT FK_Revenue_Movement FOREIGN KEY (DIM_MovementId) REFERENCES DIM_Movement(DIM_MovementId),
    CONSTRAINT FK_Revenue_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_CashCut (
    DIM_CashCutId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_ServiceDetailsId NVARCHAR(64) NOT NULL UNIQUE,
    DIM_DateId INT NOT NULL,
    DIM_ServiceOwnersId NVARCHAR(64) NOT NULL,
    DIM_CountRegisters INT NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_CashCut_ServiceDetails FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
    CONSTRAINT FK_CashCut_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_CashCut_ServiceOwners FOREIGN KEY (DIM_ServiceOwnersId) REFERENCES DIM_ServiceOwners(DIM_ServiceOwnersId)
);

CREATE INDEX IX_DIM_Customer_Fraction_EndDate ON DIM_Customer(CustomerFraction, CustomerEndDate);
CREATE INDEX IX_DIM_Account_Customer_Status ON DIM_Account(DIM_CustomerId, DIM_StatusId);
CREATE INDEX IX_FACT_Revenue_Account_ServiceDetails ON FACT_Revenue(DIM_AccountId, DIM_ServiceDetailsId);
CREATE INDEX IX_FACT_Revenue_Date ON FACT_Revenue(DIM_DateId);
CREATE INDEX IX_DIM_ServiceDetails_Service_Date ON DIM_ServiceDetails(DIM_ServiceId, DIM_DateId);
```

### 5.2 Plantilla T-SQL Exacta para las 10 Vistas (`backend/sql/02_views_tsql.sql`)

1. **`SecurityUsers`**:
```sql
CREATE OR ALTER VIEW SecurityUsers AS
SELECT
    CONCAT(cust.CustomerName, N' ', cust.CustomerMiddleName, N' ', cust.CustomerLastName, N' ', cust.CustomerSecondLastName) AS fullname,
    cust.username,
    cust.[password],
    rol.RoleName,
    s.ServiceName,
    cust.CustomerFraction,
    stat.StatusName,
    srvon.StartDate,
    srvon.EndDate,
    srvon.DIM_ServiceOwnersId,
    cust.DIM_CustomerId,
    acc.DIM_AccountId
FROM DIM_Account acc
JOIN DIM_Customer cust ON acc.DIM_CustomerId = cust.DIM_CustomerId
JOIN DIM_ServiceOwners srvon ON srvon.DIM_CustomerId = cust.DIM_CustomerId
JOIN DIM_Service s ON s.DIM_ServiceId = srvon.DIM_ServiceId
JOIN DIM_Role rol ON acc.DIM_RoleId = rol.DIM_RoleId AND rol.RoleType = N'administrador'
JOIN DIM_Status stat ON acc.DIM_StatusId = stat.DIM_StatusId;
```

2. **`VISTA_CLIENTES_ACTIVOS`**:
```sql
CREATE OR ALTER VIEW VISTA_CLIENTES_ACTIVOS AS
SELECT
    c.CustomerName, 
    c.CustomerMiddleName, 
    c.CustomerLastName, 
    c.CustomerSecondLastName,
    c.CustomerFraction,
    r.RoleName, 
    a.DIM_AccountId,
    c.DIM_CustomerId
FROM DIM_Account a
INNER JOIN DIM_Role r ON r.DIM_RoleId = a.DIM_RoleId
INNER JOIN DIM_Customer c ON c.DIM_CustomerId = a.DIM_CustomerId
INNER JOIN DIM_Status s ON a.DIM_StatusId = s.DIM_StatusId 
WHERE c.CustomerEndDate = N's/n'
AND a.DIM_StatusId IN (
    SELECT DIM_StatusId 
    FROM DIM_Status 
    WHERE StatusName = N'activo'
);
```

3. **Plantilla para `VISTA_PAGOS_<MODULO>` (`AGUA`, `DELEGACION`, `FERIA`, `PANTEON`)**:
```sql
CREATE OR ALTER VIEW VISTA_PAGOS_AGUA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN (SELECT COUNT(DIM_AccountId) FROM DIM_Account WHERE DIM_CustomerId = vw.DIM_CustomerId AND DIM_StatusId = N'status1') > 0 THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
WHERE vw.ServiceName = N'agua' 
AND vw.Ranking = 1;
```
*(En las 4 `VISTA_PAGOS_DETALLADO_<MODULO>` se usa el mismo CTE pero en el `SELECT` final se quita `AND vw.Ranking = 1`, se hace `JOIN DIM_Customer AS clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId` y `StatusCuenta` evalúa `WHEN clientes.CustomerEndDate = N's/n' THEN N'activo' ELSE N'inactivo'`).*

### 5.3 Seeds y Generación del Calendario 2021–2030 (`03_seed_tsql.sql` y Migración)
1. **`03_seed_tsql.sql`**:
   - Incluye los **8 estados** de `DIM_Status`: `status1` (`activo`), `status2` (`inactivo`), `status3` (`trabajado`), `status4` (`completo`), `status5` (`pendiente`), `status6` (`requerido`), `status7` (`nousado`), `status8` (`usado`).
   - Incluye los **11 roles** de `DIM_Role` (con `N'pequeño propietario'`).
   - Incluye los **2 movimientos** (`ingreso`, `egreso`) y los **6 servicios** (`agua`, `feria`, `panteon`, `delegacion`, `personas`, `delegado`).
2. **Población de `DIM_Date` (2021 a 2030)**:
   - Tanto en `migrate_sqlite_to_mssql.py` como en el fixture de tests, poblar `DIM_Date` para los años **2026 a 2030** con `generar_anio_real(year)` para que `DIM_DATE().dateId` nunca sea `None`.

---

## 6. SPEC-05: Suite de Pruebas End-to-End (E2E) Sin Mocks contra SQL Server Real

Crear la carpeta `backend/src/test/test_e2e_sqlserver/` con 5 archivos:
1. **`conftest.py`**:
   - Verifica que el año actual (2026) esté en `DIM_Date`.
   - Fixture `cleanup_e2e_records(autouse=True)` que borra en orden inverso de FKs cualquier fila con prefijo `e2e_%` antes y después de cada test.
   - Fixture `client` con `app.test_client()`.
2. **`test_01_pool_and_concurrency.py`**:
   - `test_connection_connects_to_sqlserver_engine`
   - `test_pool_reuses_physical_connection_and_checks_in` (verifica `@@SPID` y `get_pool_status()`)
   - `test_pool_does_not_exhaust_after_100_sequential_repository_calls` (llama 100 veces a las funciones cuyos leaks fueron cerrados y verifica `checkedout == 0`)
   - `test_pool_concurrent_threads_stress` (`ThreadPoolExecutor(max_workers=12)` con 60 operaciones concurrentes)
   - `test_uncommitted_changes_rollback_on_close_conexion`
3. **`test_02_atomic_transactions.py`**:
   - `test_insert_onwer_info_atomic_rollback_on_step3_failure` (verifica que el `UPDATE` en `DIM_Account`, el `INSERT` en `DIM_Account` y el `UPDATE` en `DIM_Customer` hagan rollback real si falla `insert_service_owner_info`).
   - `test_insert_onwer_info_atomic_commit_success`
   - `test_cash_cut_atomic_rollback_when_cash_cut_insert_fails` (verifica que `insert_many_fact_revenues` haga rollback completo si falla el `INSERT` en `DIM_CashCut`).
   - `test_checklist_payments_atomic_rollback_on_status_update_failure`
4. **`test_03_views_and_dialect_queries.py`**:
   - `test_all_10_views_execute_without_tsql_errors`
   - `test_payment_processor_year_cast_join_works_in_sqlserver`
   - `test_home_info_concat_and_users_filter_not_equal_sn`
   - `test_realtime_search_top_50_and_case_insensitive`
   - `test_analytics_isnull_and_cross_year_queries`
5. **`test_04_security_and_e2e_endpoints.py`**:
   - `test_e2e_legacy_md5_login_auto_upgrades_to_scrypt_in_sqlserver`
   - `test_e2e_full_customer_account_service_payment_lifecycle`

---

## 7. Plan de Fases y Criterios de Aceptación

1. **Fase 0**: Ajustar `URL_FRONTEND` en `backend/.env`, correr línea base `pytest` y `pnpm build`, actualizar `backend/README.md` y `frontend/README.md`, y crear commit de cierre de seguridad/limpieza.
2. **Fase 1**: Convertir `backend/requirements.txt` a UTF-8 + `pyodbc==5.2.0`, crear `backend/sql/01_schema_tsql.sql`, `02_views_tsql.sql`, `03_seed_tsql.sql`, `docker-compose.yml` y `backend/scripts/migrate_sqlite_to_mssql.py`; levantar/conectar a SQL Server local y migrar `sistema_mandho.db` + años 2026-2030.
3. **Fase 2**: Reescribir `backend/src/utils/conexion.py` (`QueuePool` + `shared_conn`) y cerrar los 12 puntos de fugas de conexión en los 9 archivos listados en §3.2.
4. **Fase 3**: Migrar los 23 archivos de `sqlite3.Error` a `pyodbc.Error`, aplicar los fixes de dialecto SQL (§4.1 y §4.2) e implementar los 3 flujos transaccionales atómicos (§3.3).
5. **Fase 4**: Implementar y ejecutar `pytest backend/src/test/test_e2e_sqlserver -v` (100% pass sin mocks contra SQL Server real).
6. **Fase 5**: Crear `backend/Dockerfile`, `backend/.dockerignore`, `frontend/public/staticwebapp.config.json` y actualizar documentación de despliegue en Azure.
