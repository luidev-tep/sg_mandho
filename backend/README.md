# Backend — S.G. Mandhò

API Flask que administra vecinos de la delegación, sus cuentas y pagos de servicios (agua, feria, panteón, delegación) sobre SQLite, con autenticación/autorización **JWT** por roles. Construida con Python y Programación Orientada a Objetos.

## Estructura del proyecto

```
backend/
├── app.py                      # Punto de entrada: app, JWT, CORS, blueprints
├── Data_Base_Schema.sql        # DDL + semillas + vistas (modelo estrella)
├── initial_information.sql     # Datos semilla (statuses, roles, movimientos, servicios)
├── Procfile                    # web: gunicorn app:app
├── requirements.txt
├── .env                        # SECRET_KEY, URL_FRONTEND, DATABASE_PATH
├── database/                   # sistema_mandho.db, schema.py, documentación generada
├── public/                     # Diagramas de arquitectura (SVG/JPG)
└── src/
    ├── routes/                 # 7 blueprints + handle_message (respuestas JSON)
    │   ├── security_route.py   # login, refresh, validaciones de contraseña
    │   ├── user_route.py       # CRUD de vecinos
    │   ├── account_route.py    # CRUD de cuentas
    │   ├── payment_route.py    # pagos, costos, corte de caja, servicios
    │   ├── analitycs_route.py  # reportes
    │   ├── search_real_time.py # búsqueda en tiempo real
    │   └── home_route.py       # datos de inicio
    ├── users/                  # UserCrud + models/user.py + repository/
    ├── accounts/               # AccountCrud + repository/ + services/validate
    ├── security/               # SecurityUsers (login, hashing, roles, decorador)
    ├── payments/               # PaymentCrud, cashCutCrud + repository/ + services/
    ├── analytics_reports/      # Analitycs + repository/ (GetAnalytics, PaymentProcesor)
    ├── fact_revenues/          # factRevenueCrud + repository/
    ├── dim_dates/              # DIM_DATE (fecha fiscal America/Mexico_City)
    ├── dim_service/            # DIM_Service, dim_servicedetails, dim_serviceonwers,
    │                           # dim_roles, dim_status, dim_movement (catálogos)
    ├── utils/                  # Conexion (SQLite), id_generator, validate_data, build_filters
    └── test/                   # 9 suites unittest (account, analytics, auth, payment, ...)
```

**Patrón**: MVC vertical por módulos con Blueprints de Flask. Capas: ruta → clase CRUD/servicio → repositorio SQL → modelo POO.

## Configuración (`app.py`)

- **L13**: `load_dotenv()` carga el `.env`.
- **L31-34**: lee `SECRET_KEY`; **aborta si no existe**; configura `JWT_SECRET_KEY`.
- **L37-40**: expiración JWT: access **20 min**, refresh **1 día**.
- **L43-49**: registro de los 7 blueprints (user, account, search, security, payment, analitycs, home).
- **L56-79**: CORS — orígenes desde `URL_FRONTEND` (lista separada por comas, default `http://localhost:5173`), métodos GET/POST/PUT/DELETE/OPTIONS/PATCH, headers Authorization, `supports_credentials=True` (`send_wildcard=False` por compatibilidad con Edge).

## Modelo de datos (esquema estrella)

Fuente de verdad: `database/sistema_mandho.db` (el `.db` vivo puede diferir del SQL).

| Tabla | Descripción | Relaciones |
|---|---|---|
| `DIM_Role` | Catálogo de roles (administrador/usuario/inactivo; 11 semillas) | — |
| `DIM_Status` | Estados: activo, inactivo, completo, pendiente, trabajado | — |
| `DIM_Date` | Calendario fiscal: `DIM_DateId` AAAAMMDD, FiscalYear (Y25), mes/trimestre/semana | — |
| `DIM_Customer` | Vecinos: nombre, fechas (nacimiento/'s/n'), dirección, manzana, credenciales | FK → DIM_Date |
| `DIM_Account` | Cuenta = pivote cliente/rol/estado con vigencia | FKs → DIM_Date, DIM_Customer, DIM_Role, DIM_Status |
| `DIM_Service` | Servicios: agua, feria, panteón, delegación, personas, delegado | — |
| `DIM_ServiceDetails` | Costo anual por tipo de servicio (consumo/tomas/faena/cooperación) | FKs → DIM_Date, DIM_Service |
| `DIM_ServiceOwners` | Asignación de comitiva/owner a un servicio | FKs → DIM_Date, DIM_Service, DIM_Customer |
| `DIM_Movement` | Tipo de movimiento: ingreso, egreso | — |
| `FACT_Revenue` | **Tabla de hechos central**: pagos con `amount` | FKs → DIM_Date, DIM_Account, DIM_ServiceDetails, DIM_Movement, DIM_Status |
| `DIM_CashCut` | Cortes de caja con nº de registros facturados | FKs → DIM_ServiceDetails (UNIQUE), DIM_Date, DIM_ServiceOwners |

**Relación central**: `FACT_Revenue` → `DIM_Account` → `DIM_Customer`/`DIM_Role`/`DIM_Status`; `DIM_DateId` conecta todo con el calendario fiscal; `DIM_ServiceDetails` fija el costo anual por servicio.

**Vistas**: `VISTA_PAGOS_AGUA`, `VISTA_PAGOS_FERIA` (CTE parametrizable), `VISTA_CLIENTES_ACTIVOS` (checklist). Los `.sqbpro` de `database/` son consultas auxiliares de DB Browser (cortes de caja, checklists, pendientes).

## Autenticación y autorización

- Login emite JWT con claims: `role`, `service`, `fraction`, `name` (`security_route.py:104-121`).
- `@jwt_required()` + `@role_required(rol)` (`src/security/security.py:555`): 403 si el rol no coincide.
- **Contraseñas y Hashing**: Las contraseñas se almacenan mediante hashes seguros generados por Werkzeug (`scrypt`). Se soporta migración transparente en login: si un usuario cuenta con un hash MD5 heredado (hexadecimal de 32 caracteres), se valida contra `hmac.compare_digest` y se actualiza automáticamente a `scrypt`. Política de contraseñas en `security.py:365`.
- **Protección contra bots**: Google reCAPTCHA v2 activo por defecto en `/api/security/login/` (`RECAPTCHA_ENABLED=true` y `RECAPTCHA_SECRET_KEY`). Puede deshabilitarse explícitamente para desarrollo local con `RECAPTCHA_ENABLED=false`.
- Revalidación de contraseña para acciones críticas: `/security/validate_password/` y `/validate_password_service/`.

## Endpoints API

Respuestas JSON estandarizadas por `send_error`/`send_success` (`src/routes/handle_message.py`): `{status, message, body}`.

> Convención: varias lecturas usan **POST** para poder pasar filtros en el body.

### Seguridad (PÚBLICO solo login)

| Método y ruta | Descripción | Auth |
|---|---|---|
| POST `/api/security/login/` | Autenticación + emisión de access/refresh JWT | — |
| POST `/api/security/refresh_token/` | Renueva el access token | Refresh JWT |
| POST `/api/security/validate_password_service/` | Revalida contraseña para acciones críticas | JWT (comitiva/subdelegado/delegado) |
| POST `/api/security/validate_password/` | Valida contraseña del delegado contra hash | JWT (comitiva) |
| POST `/api/security/admin_onwer/` | Lista administradores (`get_onwers_info`) o crea owner (`create_onwer`: elegibilidad, unicidad de cargo, hash) | Delegado |

### Personas (`/api/user`)

| Método y ruta | Descripción | Auth |
|---|---|---|
| POST `/api/user/create_user/` | Crea vecino; subdelegado solo en su manzana | Delegado/Subdelegado |
| POST `/api/user/read_user/` | Lee usuarios por `id_user` o `filters`; subdelegado filtrado a su fracción | Delegado/Comitiva/Subdelegado |
| POST `/api/user/update_user/` | Edita dirección/manzana/número (bloquea admins y fallecidos) | Delegado/Subdelegado |
| PATCH `/api/user/delete_user/` | "Defunción": baja lógica; **409** si tiene pagos pendientes | Delegado/Subdelegado |
| GET `/api/user/gat_data/` | Historial de pagos de un cliente (`?Dim_customerId=`) | Delegado/Subdelegado/Comitiva |

### Cuentas (`/api/account`)

| Método y ruta | Descripción | Auth |
|---|---|---|
| POST `/api/account/create/` | Crea cuenta (rol + estado + vigencia) para un cliente | Delegado/Subdelegado |
| POST `/api/account/read/` | Lee cuentas (una, todas, o por filtros) | Delegado/Subdelegado/Comitiva |

### Búsqueda

| Método y ruta | Descripción | Auth |
|---|---|---|
| GET `/api/search/search_client/` | Búsqueda en tiempo real (`?q=`, mín. 3 caracteres, LIKE, LIMIT 50, excluye fallecidos) | Delegado/Comitiva/Subdelegado |

### Pagos (`/api/payment`)

| Método y ruta | Descripción | Auth |
|---|---|---|
| POST `/api/payment/create/` | Crea pago individual o masivo (lista = checklist); comitiva limitada a su servicio | Comitiva (según token) |
| POST `/api/payment/read/` | Lee pagos por `filters` o `DIM_CustomerId`; delegado requiere serviceName | Delegado/Comitiva |
| POST `/api/payment/get_cost/` | Costo de un servicio para un cliente/año | Comitiva |
| POST `/api/payment/get_any_data/` | Caja genérica: `costoservicio`, `pagosPendientes`, `servicios_corte_caja` | Delegado/Comitiva/Subdelegado |
| POST `/api/payment/cash_cut/` | Corte de caja: factura (amount=0) a todos los pendientes del servicio + registro DIM_CashCut. **No permitido para agua** | Comitiva |
| POST `/api/payment/generar_servicio/` | Crea/renueva el costo anual (DIM_ServiceDetails) | Comitiva |

### Analíticas e inicio

| Método y ruta | Descripción | Auth |
|---|---|---|
| POST `/api/analitycs/get_analytics/` | Ingresos por año, facturas por mes/comitiva, población por manzana, pagos por usuario, admins | Delegado/Comitiva |
| GET `/api/home/get_home_info` | Datos de administradores para la pantalla de inicio | Delegado/Comitiva/Subdelegado |

## Clases principales

| Clase | Archivo | Responsabilidad |
|---|---|---|
| `Conexion` | `src/utils/conexion.py:4` | Conexión SQLite (WAL, busy_timeout 5000ms) |
| `create_id` | `src/utils/id_generator.py:3` | UUID5 determinista de 18 caracteres (IDs estables) |
| `validate_data` | `src/utils/validate_data.py:1` | Validación de campos/tipos de cada payload |
| `BuildFilters` | `src/utils/build_filters.py:3` | Construcción dinámica de filtros SQL (fechas fiscales, manzanas) |
| `DIM_DATE` | `src/dim_dates/dim_date.py:11` | Fecha fiscal America/Mexico_City, `dateId` AAAAMMDD, edad |
| `UserCrud` | `src/users/user.py:31` | CRUD de vecinos + `defuncion_user` (bloqueo por adeudos) |
| `AccountCrud` | `src/accounts/account.py:28` | Insert/read/desactivate de cuentas |
| `SecurityUsers` | `src/security/security.py:40` | Login, hashing, reglas de unicidad de cargos, política de contraseñas |
| `role_required` | `src/security/security.py:498` | Decorador de autorización por rol |
| `PaymentCrud` | `src/payments/payment.py:39` | Pagos individuales/masivos, costos, pendientes |
| `cashCutCrud` | `src/payments/cash_cut.py:31` | Corte de caja (factura pendientes con amount=0) |
| `ValidatePayment` | `src/payments/services/validate_payment.py:10` | Validaciones de pago/cuenta activa, pagos duplicados |
| `Analitycs` | `src/analytics_reports/Analitycs.py:5` | Reportes por servicio y por cliente |
| `factRevenueCrud` | `src/fact_revenues/Fact_revenue.py:27` | Facturación: valida monto, determina status según amount |
| `ServiceDetailsCrud` | `src/dim_servicedetails/serviceDetails.py:20` | Alta/renovación de costos anuales |

Los modelos POO (`User`, `DIM_Account`, `FACT_Revenue`, `DIM_DATE_MODEL`, etc.) están en las carpetas `models/` de cada módulo.

## Dependencias (`requirements.txt`)

| Librería | Uso |
|---|---|
| Flask 3.1.0 | Framework web + blueprints |
| Flask-JWT-Extended 4.7.1 | JWT access/refresh y claims |
| flask-cors 5.0.1 | CORS global (incl. Edge) |
| python-dotenv 1.1.0 | Carga de variables `.env` |
| gunicorn 23.0.0 | Servidor WSGI de producción (Procfile) |
| pytz 2025.2 / zoneinfo | Zona horaria America/Mexico_City |
| requests 2.32.3 | Google reCAPTCHA v2 (activo por defecto, desactivable con RECAPTCHA_ENABLED=false) |
| sqlite3 (stdlib) | Persistencia: SQL manual sin ORM |
| pytest 8.4.1 | Runner de los tests de `src/test/` |

> **Nota**: SQLAlchemy y Flask-SQLAlchemy están en requirements pero **no se usan** en el código.

## Despliegue

- **Procfile**: `web: gunicorn app:app` (Heroku/Railway style).
- **Desarrollo**: `python app.py` (con `debug=True`; desactivar en producción).
- **Variables de entorno**: `SECRET_KEY` (obligatoria), `URL_FRONTEND` (orígenes CORS), `DATABASE_PATH`.
- **BD inicial**: ejecutar `Data_Base_Schema.sql` y `initial_information.sql`.

## Test

```powershell
venv\Scripts\activate
pytest src/test -v
```

Suites: `account`, `analytics`, `auth`, `dim_dates`, `payment`, `role`, `services`, `user`, `utils`.

## Diagramas

- `classes_Backend_diagram_Class.svg` (raíz): UML de clases del backend.
- `packages_Backend_diagram_Class.svg` (raíz): grafo de dependencias entre paquetes de `src/`.
- `public/classes_Backend_diagram_App.svg` y `public/packages_Backend_diagram_App.svg`: versiones que incluyen la app y sus 6 rutas.

## Observaciones técnicas

1. Lecturas vía **POST** (filtros en body) — convención mantenida por compatibilidad de contratos con el frontend.
2. **Hashing de contraseñas**: Migrado a `Werkzeug scrypt` con soporte de migración transparente y en caliente de hashes MD5 legados en el primer inicio de sesión.
3. **reCAPTCHA**: Implementado y activo por defecto en `/api/security/login/`, controlable vía variable de entorno `RECAPTCHA_ENABLED`.
4. **Erratas heredadas preservadas**: Mantienen estricta compatibilidad con frontend y esquema de datos: `Singup.jsx`, `gat_data`, `ServiceDetailesType`, `DIM_ServiceOnwers`.
5. SQLite + gunicorn multi-worker: En proceso de migración a SQL Server con QueuePool transaccional.
