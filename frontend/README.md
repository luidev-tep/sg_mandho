# Frontend — SG Mandhò

Aplicación de una sola página para gestionar el padrón comunitario, cuentas, pagos, cortes de caja y analíticas. Está construida con React 19, Vite 6 y Tailwind CSS v4.

## Stack y capacidades

- React 19, React Router 7 y Vite 6.
- Tailwind CSS v4, formularios con React Hook Form y Yup, gráficas con Chart.js.
- Capa HTTP central con Axios, envío de JWT access tokens y renovación al recibir una respuesta 401.
- Búsqueda y tablas paginadas para el padrón; navegación adaptada a los roles delegado, subdelegado y comitiva.
- Diseño adaptable, soporte de tema y controles accesibles por teclado.

`src/config/communityConfig.js` centraliza nombre, branding y opciones geográficas de la comunidad. El componente SVG `<BrandLogo />` y la configuración de navegación usan esos valores.

## Estructura

| Ruta | Contenido |
|---|---|
| `src/api/` | Servicios HTTP e instancia Axios compartida |
| `src/components/` | Componentes comunes, paginación, búsqueda y formularios |
| `src/pages/` | Login, personas, cuentas, pagos y perfil |
| `src/partials/` | Layout, navegación y dashboard |
| `src/config/` | Configuración centralizada de la comunidad |

## Configuración

Copia `frontend/.env.example` como `frontend/.env` y define:

- `VITE_API_URL`: URL base del backend, por ejemplo `http://127.0.0.1:5000/api/`.
- `VITE_RECAPTCHA_SITE_KEY`: clave pública de reCAPTCHA v2.
- `VITE_RECAPTCHA_ENABLED`: activa o desactiva el desafío en la interfaz; en producción se requiere una clave de sitio válida.
- `VITE_ENVIRONMENT`: etiqueta de entorno usada por la configuración del cliente.

La configuración de Azure Static Web Apps está en `frontend/public/staticwebapp.config.json`. Define el fallback de rutas SPA, exclusiones para assets y headers HTTP; no define una política CSP.

## Desarrollo y build

Desde la raíz:

~~~powershell
Copy-Item frontend/.env.example frontend/.env
pnpm --dir frontend install
pnpm --dir frontend dev
pnpm --dir frontend build
~~~

Vite divide dependencias de React y React Router en `react-vendor` y las gráficas/fechas de Chart.js en `chart-vendor`. `date-fns` se usa para validación de fechas. Los chunks de producción se escriben en `frontend/dist/`.

## Rutas principales

| Ruta | Función |
|---|---|
| `/Signup` | Inicio de sesión |
| `/personas/usuarios` | Consulta, búsqueda y paginación del padrón |
| `/personas/registro` | Registro de persona |
| `/Cuentas/Cuenta` | Alta de cuenta |
| `/modulos/:moduleName` | Pagos por servicio y cortes de caja |
| `/Analytics/:comitiva` | Dashboard analítico |

El menú y las acciones visibles respetan el rol y servicio incluidos en la sesión. La configuración de zonas se obtiene de `communityConfig.js`.
