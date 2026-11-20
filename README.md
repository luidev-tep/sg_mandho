# S.G. Mandhò

## Gestión financiera y padrón comunitario con analítica

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=20232A)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?logo=tailwindcss&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-Azure_SQL-CC2927?logo=microsoftsqlserver&logoColor=white)
![Flyway](https://img.shields.io/badge/Database_Migrations-Flyway-CC0200)
![Docker](https://img.shields.io/badge/Containers-Docker-2496ED?logo=docker&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-844FBA?logo=terraform&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)

**SG Mandhò** digitalizes community revenue collection, resident records, service payments and financial reporting.<br>
The platform combines a React single-page application, a Flask API and a dimensional SQL Server data model.<br>
Its cloud-ready deployment targets Azure Static Web Apps, Azure Container Apps and Azure SQL Database.<br>
This repository provides the implementation and technical documentation; detailed documentation is in Spanish.

## Problema y enfoque de ingeniería

Las comitivas comunitarias necesitan mantener un padrón vigente, registrar pagos por servicio y realizar cortes de caja con trazabilidad. SG Mandhò reúne esos flujos en una aplicación con acceso por rol, operaciones financieras transaccionales y analítica por servicio, periodo y fracción.

El diseño separa la interfaz, la API y la persistencia, mantiene el esquema bajo control de versiones y prepara la aplicación para despliegues reproducibles en Azure.

## Arquitectura cloud-ready

~~~mermaid
flowchart LR
    U[Persona usuaria] --> SWA[React 19 + Vite<br/>Azure Static Web Apps]
    SWA -->|HTTPS /api| ACA[Flask + Gunicorn<br/>JWT, scrypt, QueuePool<br/>Azure Container Apps]
    ACA -->|ODBC Driver 18 / TLS| SQL[Azure SQL Database<br/>Star schema + 10 vistas T-SQL<br/>Flyway]
    TF[Terraform<br/>infra/] -. define .-> AZ[Recursos de Azure]
    AZ -. despliega .-> SWA
    AZ -. despliega .-> ACA
    AZ -. aprovisiona .-> SQL
    GH[GitHub Actions<br/>CI/CD] -->|Flyway| SQL
    GH -->|imagen| ACA
    GH -->|frontend| SWA
~~~

### Engineering Highlights

- **Dimensional data model:** `FACT_Revenue` and 10 `DIM_*` tables support financial reporting. Ten T-SQL views use CTEs, `SUM() OVER` and `RANK() OVER` to expose service payment summaries and detail.
- **SQLite to SQL Server migration:** the backend now uses SQL Server locally and Azure SQL in the cloud. SQLAlchemy `QueuePool` manages connections; `with Conexion() as tx:` coordinates ACID units of work; Flyway versions `V*` migrations and repeatable `R__*` views.
- **Layered security:** legacy MD5 hashes upgrade progressively to scrypt on successful login; JWT access and refresh tokens, role and service-based RBAC, parameterized SQL and configurable reCAPTCHA v2 protect application flows.
- **Real-database E2E coverage:** tests run against SQL Server and verify physical connection reuse through `@@SPID`, concurrent access and a zero checked-out pool after relevant operations.
- **Modern frontend:** React 19, Tailwind CSS v4, keyboard accessibility and responsive patterns informed by Baseline and Modern Web Guidance. `communityConfig.js` centralizes community branding and geography.
- **Infrastructure and delivery:** Terraform describes Azure infrastructure, while GitHub Actions provides CI, Flyway migration and deployment workflows.

## Roles del sistema

| Rol | Alcance |
|---|---|
| **Delegado** | Administración de personas, cuentas, pagos, analíticas y administradores. |
| **Subdelegado** | Gestión y consulta de personas dentro de su fracción. |
| **Comitiva** | Operación del servicio asignado (agua, feria, panteón o delegación), incluidos pagos y cortes de caja. |

## Puesta en marcha rápida

Este flujo levanta SQL Server en Docker, aplica migraciones con Flyway, carga datos sintéticos y ejecuta la API y el frontend localmente. Requiere Docker Desktop, Python 3.13, Node.js y pnpm.

### 1. SQL Server y Flyway

En PowerShell, define una contraseña para el contenedor y levanta SQL Server:

~~~powershell
$env:MSSQL_SA_PASSWORD = Read-Host 'SQL Server SA password'
docker compose -f docker-compose.db.yml up -d sqlserver
~~~

Aplica el esquema y las vistas versionadas:

~~~powershell
docker compose -f docker-compose.db.yml --profile migrate run --rm flyway migrate
~~~

### 2. Backend y datos demo

Crea la configuración local del backend:

~~~powershell
Copy-Item backend/.env.example backend/.env
~~~

En `backend/.env`, configura la conexión Docker con SQL Server (`DB_DRIVER=ODBC Driver 18 for SQL Server`, `DB_SERVER=localhost,1433`, `DB_NAME=sg_mandho`, `DB_USER=sa`, la misma contraseña definida en `MSSQL_SA_PASSWORD`, `DB_ENCRYPT=no`, `DB_TRUST_CERT=yes` y `DB_TRUSTED_CONNECTION=no`). Para desarrollo local, establece `RECAPTCHA_ENABLED=false` y genera un valor propio para `SECRET_KEY`.

Instala dependencias del backend y carga registros ficticios. El seed crea las seis cuentas demo con la contraseña que proporciones:

~~~powershell
python -m venv backend/venv
.\backend\venv\Scripts\python.exe -m pip install -r backend/requirements.txt
$env:DEMO_ADMIN_PASSWORD = Read-Host 'Contraseña de cuentas demo (mínimo 8 caracteres)'
.\backend\venv\Scripts\python.exe backend\scripts\seed_demo_azure.py
Remove-Item Env:DEMO_ADMIN_PASSWORD
~~~

Inicia la API en una terminal:

~~~powershell
Set-Location backend
.\venv\Scripts\python.exe app.py
~~~

La API estará disponible en `http://127.0.0.1:5000`; el endpoint de estado es `http://127.0.0.1:5000/health`.

### 3. Frontend

En otra terminal:

~~~powershell
Copy-Item frontend/.env.example frontend/.env
Set-Location frontend
pnpm install
pnpm dev
~~~

Configura `VITE_API_URL=http://127.0.0.1:5000/api/` y, si no usarás reCAPTCHA en local, `VITE_RECAPTCHA_ENABLED=false`. Vite sirve la aplicación en `http://localhost:5173`.

## Demo en vivo y capturas

**Azure Static Web Apps:** `https://<nombre-de-la-app>.azurestaticapps.net` — pendiente de publicar o configurar.

Cuando estén disponibles capturas reales, se pueden añadir en `docs/screenshots/`, por ejemplo `dashboard.png`, `payments.png`, `people-registry.png` y `cash-cut.png`.

## Documentación del proyecto

- [Backend: API, configuración y pruebas](backend/README.md)
- [Frontend: aplicación, configuración y build](frontend/README.md)
- [Base de datos y migraciones Flyway](backend/db/README.md)
- [Guía de despliegue en Azure](docs/guia_despliegue_azure.md)
- [Bitácora técnica de la migración a SQL Server](docs/bitacora_tecnica_migracion_sqlserver.md)
- [Infraestructura como código con Terraform](infra/)

## Roadmap White-Label (Post-v1)

- Incorporar `DIM_CommunityConfig` para separar identidad y configuración por comunidad.
- Incorporar `DIM_Fraction` para administrar fracciones desde el modelo de datos.
- Unificar las vistas de pagos por servicio con una definición parametrizable.
- Generar recibos PDF y ofrecer consulta e impresión desde la aplicación.

## Agradecimientos

Agradezco la mentoría técnica y el acompañamiento recibidos durante la etapa inicial del proyecto; contribuyeron a consolidar sus fundamentos de arquitectura y desarrollo.

## Licencia

Distribuido bajo licencia MIT. Consulta [LICENSE](LICENSE).
