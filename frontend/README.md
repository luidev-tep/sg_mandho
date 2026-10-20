# Frontend — S.G. El Mandhó

SPA (React 19 + Vite 6 + TailwindCSS v4) para la gestión comunitaria: personas, cuentas, pagos por servicio, cortes de caja y analíticas. Basada en la plantilla "Mosaic" (Cruip) adaptada al proyecto.

## Stack y dependencias

| Tecnología | Versión | Uso |
|---|---|---|
| React | ^19.0.0 | Framework UI |
| Vite | ^6.0.11 | Build tool (+ `@vitejs/plugin-react`) |
| react-router-dom | ^7.1.5 | Enrutado SPA |
| TailwindCSS | ^4.0.2 (+ forms) | Estilos utility-first |
| axios | ^1.10 | Cliente HTTP |
| react-hook-form + yup | ^7.58 | Formularios y validación |
| chart.js + moment | ^4.4.7 | Gráficas del dashboard |
| clsx + tailwind-merge | — | Helper `cn()` (`src/lib/utils.js`) |
| @radix-ui/react-popover, react-day-picker | — | Calendario/datepicker |
| react-google-recaptcha | ^3.1 | Anti-bot en login |
| react-transition-group | — | Animaciones (`utils/Transition.jsx`) |

**Estado**: sin Redux/Zustand — Context API nativo (`AuthContext`, `ThemeContext`).
**Gestor de paquetes**: pnpm.
**Scripts** (`package.json`): `dev` = `vite --host 0.0.0.0` · `build` = `vite build` · `preview` = `vite preview`.

## Estructura de carpetas (`src/`)

| Carpeta | Propósito |
|---|---|
| `api/` | Capa de servicios HTTP: una función por endpoint, todas unificadas sobre la instancia central con interceptor de refresco JWT (`src/api/axiosInstance.js`) |
| `charts/` | 10 wrappers de Chart.js (`BarChart02/03/04`, `LineChart03/04`, `Doughnut`, `Pie`, `Polar`, `BarchartFraction`) + `ChartjsConfig.jsx` |
| `components/` | UI reutilizable: modales (`ModalBlank`, `Modalmessaje`, `ModalValitePass`, `ModalSearch`), selects/dropdowns, `PaginationClassic`, `LoadingSpinner` |
| `components/accounts/` | Búsqueda de cliente y cuentas (`GetAccount`, `AccounsTable`) |
| `components/alertas/` | `FormattedErrorMessage` |
| `components/customers/` | `BarraBusqueda`, edición/reporte/desactivación de personas |
| `components/modules/` | Flujo de pagos: `TerminarPago`, `DynamicServiceModules/GenericServicePayment`, `tablas/` (`DynamicTable`, `CorteCajaModal`), `UsersPayment/`, y JSONs de configuración en `crear/` (`crear_agua.json`, `crear_feria.json`, `crear_panteon.json`, `crear_delegacion.json`) |
| `components/ui/` | Shadcn-style: `calendar.jsx`, `popover.jsx`, `Notification.jsx` |
| `css/` | `style.css` (entrada Tailwind v4) + `additional-styles/utility-patterns.css` |
| `images/` | ~150 assets de la plantilla (varios sobrantes) |
| `lib/` | `utils.js` con `cn()` |
| `pages/` | Vistas enrutadas: subcarpetas `cuentas/`, `payments/`, `personas/` |
| `partials/` | Layout: `SideBar.jsx` (menú por rol), `Header.jsx` (búsqueda global + tema) |
| `partials/analytics/` | Cards del dashboard (`DashboardCard*`, `FintechCard*`, `AnalyticsButton`…) |
| `partials/customers/` | `CustomersTable` + item |
| `utils/` | `AuthContext.jsx`, `ThemeContext.jsx`, `IdleTimeoutModal.jsx`, `useDebounce.js`, `Utils.js` (moneda/colores) |

## Rutas de la app

Definidas en `src/App.jsx:71-96` con `BrowserRouter` (montado en `main.jsx`).

| Ruta | Componente | Vista |
|---|---|---|
| `/` y `/CompanyProfile` | `CompanyProfile` | Perfil de la comunidad (delegado/subdelegados/comitivas) |
| `/Signup` | `Singup` *(typo heredado)* | **Login** con reCAPTCHA |
| `/personas/usuarios` | `personas/Customers` | Tabla de personas con filtros y búsqueda global |
| `/personas/registro` | `personas/UseRegister` | Registro de persona (react-hook-form + yup) |
| `/personas/registro_exito/:id` | `personas/UserSucces` | Confirmación de registro |
| `/Cuentas/Cuenta` | `cuentas/Cuenta` | Creación de cuenta para un cliente |
| `/modulos/:moduleName` | `payments/DynamicMenu` | Menú de pagos por servicio (agua, panteón, delegación, feria) |
| `/modulos/servicio/:moduleName` | `payments/DynamicMenu` | Variante "servicio" |
| `/modulos/crear_pago/:moduleName` | `payments/DynamicGeneratePay` | Wizard de creación de pago (carga perezosa) |
| `/modulos/estado_pago` | `payments/PaymentStatus` | Resultado del pago (querystring) |
| `/modulos/usuarios/:moduleName` | `payments/DynamicMostrarUsuarios` | Personas del módulo con pagos |
| `/modulos/crear_servicio/:moduleName` | `payments/AgregarServicio` | Alta de servicio anual (requiere verificar contraseña) |
| `/Analytics/:comitiva` | `Analytics` | Dashboard por comitiva |
| `/modulos/agregar_administrador/` | `AgregarUsuario` | Alta de usuarios administrativos |

**Lógica de roles en el menú** (`SideBar.jsx:22-81`): `comitiva` solo ve su servicio; `delegado` no ve crear_pago/usuarios; `subdelegado` está limitado a su manzana.

## Comunicación con el backend

### Configuración (`.env`)

- `VITE_API_URL` — baseURL (dev: `http://127.0.0.1:5000/api/`; producción: Railway, comentada).
- `VITE_RECAPTCHA_SITE_KEY`
- `VITE_ENVIRONMENT`

### Instancia central axios

Todas las peticiones utilizan la **instancia central** `src/api/axiosInstance.js`:
- `baseURL = import.meta.env.VITE_API_URL` (L6-8).
- **Interceptor de petición** (L11-34): añade `Authorization: Bearer <access>` desde `localStorage['tokens']`.
- **Interceptor de respuesta** `setupInterceptors` (L37-82): ante 401 → llama `RefrescarToken(refresh_token)` → reintenta la petición original con el nuevo token; si la renovación falla → emite `CLEAR_USER` y redirige al login.
- *(La antigua segunda instancia duplicada en `src/api/pagos/axiosInstance.js` fue retirada para garantizar renovación consistente en todos los módulos).*

### Archivos de API (uno por endpoint)

| Archivo | Endpoints |
|---|---|
| `api_auth.js` | `security/login/`, `security/refresh_token/` |
| `api_user.js` | `user/create_user/`, `read_user/`, `update_user/`, `delete_user/` (PATCH), `home/get_home_info`, historial en `user/gat_data/` |
| `api_account.js` | `account/create/`, `account/read/` |
| `api_busqueda_persona.js` | `search/search_client/?q=` (desde L67, GET con AbortSignal) |
| `api_administrador.js` | `security/admin_onwer/` |
| `api_security.js` | `security/validate_password/`, `validate_password_service/` |
| `api_analiticas.js` | `analitycs/get_analytics/` (POST con comitiva/mes/año en formato `Y25`) |
| `pagos/api_crear_pago.js` | `payment/create/`, `payment/cash_cut/` |
| `pagos/api_mostrar_pago.js` | `payment/read/` |
| `pagos/api_get_costo_servicio.js` | `payment/get_cost/`, `getPagosPendientes`, `Get_servicios_disponibles` |
| `pagos/api_generar_servicio.js` | `payment/generar_servicio/` |

Patrón común: validar payload → llamar con la instancia central → normalizar la respuesta `{status, message, body}` del backend → mapear errores a mensajes legibles.

## Autenticación (`src/utils/AuthContext.jsx`)

1. **Login**: `ObtenerUsuario()` → POST `security/login/` con `username/password/RoleName/manzana/recaptcha` → dispatch `SET_USER_AND_TOKENS` (`Singup.jsx:47-53`).
2. **Persistencia**: reducer con `localStorage` — usuario expira a las **3 h**, tokens a las **24 h** (`AuthContext.jsx:17-43`).
3. **Renovación proactiva**: cada 15 min con `security/refresh_token/` (Bearer = refresh token) — `AuthContext.jsx:203-227`.
4. **Inactividad**: 15 min → modal `IdleTimeoutModal` con cuenta atrás de 3 min → logout.
5. **Guard global**: efecto que redirige a `/Signup` si falta usuario o tokens (`AuthContext.jsx:230-239`).
6. **Logout** desde `DropdownProfile.jsx:27-30` (`CLEAR_USER` + navigate).

## Configuración

- **`vite.config.js`**: plugin React; server en `0.0.0.0:5173`; esbuild elimina `console`/`debugger` en producción (L11-13).
- **`postcss.config.cjs`**: solo `@tailwindcss/postcss` (entrada `src/css/style.css`).
- **`src/css/style.css`**: Tailwind v4 (`@import 'tailwindcss'`), plugin forms, variantes custom `dark` y `sidebar-expanded`, paleta `@theme` con fuente Inter.
- **`eslint.config.js`**: flat config con `react-hooks` y `react-refresh`; `no-unused-vars` ignora `^[A-Z_]`.
- **`index.html`**: tema dark de `localStorage` aplicado inline antes del render; título "S.G. El Mandhó".

## Puesta en marcha

```powershell
pnpm install
# .env: VITE_API_URL, VITE_RECAPTCHA_SITE_KEY, VITE_ENVIRONMENT
pnpm dev      # http://localhost:5173
pnpm build    # build de producción en dist/
```

## Notas técnicas

1. Errata heredada preservada: página de login llamada `Singup.jsx` (debe mantenerse intacta por compatibilidad de rutas y contratos existentes).
2. `components/Lista.jsx`: eliminado del árbol de componentes por código huérfano.
3. `react-toast`: desinstalado y depurado de `package.json`.
4. Instancias axios: unificadas en `src/api/axiosInstance.js`, garantizando ciclo de vida JWT consistente en pagos y analíticas.
5. Favicon: corregido y servido desde `/favicon.png`.
6. Flujo ágil pendiente: impresión y tickets por módulo (ver roadmap en secciones anteriores del proyecto).
