# Despliegue de SG Community en Azure

La demo usa Static Web Apps, Azure Container Apps, Azure Container Registry y
Azure SQL con autenticación exclusiva de Microsoft Entra. La aplicación accede
a SQL mediante `uai-sg-community-backend`. El reCAPTCHA usa un secreto en
`kv-sg-community-536e`, referenciado por la aplicación con esa identidad.

## Estado de Terraform

El backend `azurerm` almacena el estado en el contenedor privado `tfstate` de
`sgcommunitytfstate536e`, con autenticación Entra y bloqueo de blob. El recurso
se preparó por separado para evitar que Terraform destruya su propio backend.
La cuenta tiene claves compartidas deshabilitadas, versionado y retención de
eliminaciones. Conceda al operador `Storage Blob Data Contributor` en la cuenta
de almacenamiento antes de ejecutar `terraform init`. El estado contiene datos
sensibles: no lo descargue ni lo añada a Git. Los planes y copias locales también
son sensibles y están ignorados por Git.

El estado remoto y las copias históricas pueden contener el secreto Flask y la
antigua contraseña del administrador SQL, incluso con autenticación Entra-only.
La configuración actual todavía recibe esas variables sensibles al planificar.
La imagen del backend se despliega por GitHub Actions y Terraform ignora cambios
en su etiqueta para no revertirla. No aplique un plan sin revisar todos sus cambios.

## Secretos

El secreto `recaptcha-secret` de Key Vault se referencia sin versión mediante
la identidad administrada del backend. `RECAPTCHA_ENABLED=true` y
`RECAPTCHA_SECRET_KEY` apunta al secreto de Container Apps, no al valor en Git.
La clave de sitio es pública y se incluye durante la compilación del frontend.
Autorice cada dominio utilizado en la consola de Google reCAPTCHA.

## Despliegue

El workflow manual `Deploy Azure` usa OpenID Connect con la identidad
`uai-sg-community-github`, limitada a `main`. Primero ejecuta Flyway con Entra;
solo si la migración pasa construye la imagen, actualiza Container Apps y
publica el frontend. Requiere conectividad del runner a Azure SQL y un usuario
de base de datos para la identidad de despliegue. Las variables de GitHub
identifican la suscripción, los recursos y la clave pública; el token de
publicación de Static Web Apps está en GitHub Secrets. No se emplea una
contraseña SQL ni un secreto de cliente Entra.

El despliegue automático debe validarse con una ejecución manual antes de
considerarlo operativo. Mantenga el historial de migraciones y no ejecute un
baseline automático sobre una base existente.

## Usuarios demo

`backend/scripts/seed_demo_azure.py` inserta seis administradores y datos
sintéticos; exige `DEMO_ADMIN_PASSWORD` en el entorno, de al menos ocho
caracteres. Los seis usuarios comparten esa contraseña. Repetir el seed no
actualiza contraseñas existentes. Ejecútelo únicamente contra una base demo
migrada, con acceso Entra y conectividad autorizada temporalmente. Las cuentas
sembradas son válidas para 2026. No incluya contraseñas en Git, logs ni chat.

Después de desplegar, verifique `/health`, el inicio de sesión con reCAPTCHA,
la navegación, los pagos y las analíticas. Para validar el arranque en frío,
compruebe además la respuesta después de la pausa de SQL y Container Apps.
