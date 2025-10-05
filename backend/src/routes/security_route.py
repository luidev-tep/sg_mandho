import requests  # Necesitarás esta librería para hacer la petición a Google
import os        # Para manejar variables de entorno de forma segura

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token,
    create_refresh_token
)
from typing import Any
from flask import Blueprint, request
from src.users.user import UserCrud
from src.routes.handle_message import send_error, send_success
from src.security.security import SecurityUsers, role_required

user_options = UserCrud()
security_options = SecurityUsers()


from src.security.repository.get_onwers_info import get_securyty_users_info

security_route = Blueprint('security_route', __name__, url_prefix='/api/security/')

# 1. Obtener información de la URL como PARÁMETROS DE RUTA
#    Ejemplo de URL: /api/auth/read_user/123 (donde 123 es el user_id)
# 1. Obtener información de la URL como PARÁMETROS DE RUTA
#    Ejemplo de URL: /api/auth/read_user/123 (donde 123 es el user_id)
@security_route.route('login/', methods=['POST'])
def login() -> tuple[Any]:# -> tuple[Response, Literal[404]] | Any | tuple[Response, Lit...:
    """
    Endpoint principal para la autenticación de usuarios y generación de tokens JWT.

    Este endpoint maneja el proceso de inicio de sesión de un usuario. Espera recibir
    credenciales de usuario (probablemente nombre de usuario/correo y contraseña)
    en el cuerpo JSON de la solicitud.

    Flujo de ejecución:
    1. **Validación de Datos:** Verifica si se recibió el cuerpo JSON.
    2. **Autenticación (security_options.authenticate_user):** Llama a la lógica de negocio
       para verificar las credenciales del usuario.
    3. **Manejo de Error de Autenticación:** Si la autenticación falla (estado != 200),
       retorna un error con el mensaje y estado correspondientes.
    4. **Generación de JWT:** Si la autenticación es exitosa, se generan dos tokens:
       - **Access Token:** Token de corta duración utilizado para proteger las rutas de la API.
         Incluye el `DIM_ServiceOwnersId` como `identity` y añade **claims adicionales**:
         'role', 'service', y 'fraction' del usuario.
       - **Refresh Token:** Token de larga duración utilizado únicamente para obtener
         un nuevo access token cuando este expire. También incluye las mismas claims.
    5. **Respuesta:** Empaqueta los datos del usuario (`user_data`) y los tokens JWT
       generados en un solo diccionario y los retorna en una respuesta de éxito (200).

    JSON Body esperado (ejemplo):
    {
      "username": "usuarioejemplo",
      "password": "mi_contraseña_segura"
      // La parte de reCAPTCHA está actualmente comentada para deshabilitar temporalmente
      // la validación de bots, pero su estructura de validación se mantiene en los comentarios.
    }

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que contiene los datos del
                  usuario autenticado y sus tokens de acceso y refresco.
    """
    
    try:
        data_json = request.json
        if not data_json:
            return send_error("No se recibieron datos", 400)
        
        """
        #SE DESACTIVARA TODA ESTA PARTE YA QUE POR EL MOMENTO NO ES CRUCIAL, PERO SI SE DEBE TENER CUIDADO
        # --- 1. VALIDACIÓN DEL TOKEN RECAPTCHA ---
        recaptcha_token = data_json.get('recaptcha')
        if not recaptcha_token:
            return send_error("El token de reCAPTCHA es requerido.", 400)

        # Tu clave secreta de reCAPTCHA. NUNCA la pongas directamente en el código.
        # Guárdala como una variable de entorno.
        recaptcha_secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
        if not recaptcha_secret_key:
            # Error para el desarrollador, no para el usuario final
            print("ERROR: La variable de entorno RECAPTCHA_SECRET_KEY no está configurada.")
            return send_error("Error de configuración en el servidor.", 500)

        # Petición a la API de Google para verificar el token
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': recaptcha_secret_key,
                'response': recaptcha_token
            }
        )
        response_data = response.json()

        # Verificamos si Google aprobó la solicitud y si la puntuación es aceptable
        # El umbral de 0.5 es un buen punto de partida, pero puedes ajustarlo.
        if not response_data.get('success') or response_data.get('score', 0.0) < 0.5:
            print(f"Fallo de reCAPTCHA: {response_data.get('error-codes', 'Puntuación baja')}")
            return send_error("Verificación de reCAPTCHA fallida. Inténtalo de nuevo.", 401)
        """        
        estado, mensaje, user_data = security_options.authenticate_user(data_json)
        
        if estado != 200:
            return send_error(mensaje, estado)
        
        #Logica de generacion de JWT
        access_token = create_access_token(
            identity=user_data['DIM_ServiceOwnersId'],
            additional_claims={
            "role": user_data['RoleName'],
            "service": user_data['ServiceName'],
            "fraction": user_data['CustomerFraction'],
            "name": user_data['username']
                        }
            )
        refresh_token = create_refresh_token(
            identity=user_data['DIM_ServiceOwnersId'],
            additional_claims={
            "role": user_data['RoleName'],
            "service": user_data['ServiceName'],
            "fraction": user_data['CustomerFraction'],
            "name": user_data['username']
                        }
            )
        #Es la mejor forma de enviar la informacion ya que no se cambia nada, slamente se modifica el diccionario interno
        data = {
            'data': user_data,
            'tokens': {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }
        
        #se empquetan en un diccionario para despues volver a desempaquetarse y enviarse en el cuerpo de la peticion
        #Se tuvo que hacer una modificaciona la funcion de Send Succes
        return  send_success(mensaje,data,200)
    except Exception as e:
        print(f"Error al obtener el usuario por ID: {e}")
        return send_error(str(e), 500)


@security_route.route('validate_password_service/', methods=['POST'])
@jwt_required()
def validar_password_by_action() -> tuple[Any]:
    """
    Endpoint para validar una contraseña de forma aislada.

    Este endpoint se utiliza para verificar una contraseña específica (hardcodeada
    como 'qwerty' en la lógica actual) para una funcionalidad secundaria, como
    una doble verificación de seguridad antes de una acción crítica (ej. un corte de caja).

    Restricción de Acceso:
    - Solo usuarios con el rol **'comitiva'** pueden acceder a esta ruta (debido al decorador `@role_required('comitiva')`).

    Flujo de ejecución:
    1. **Validación de Datos:** Verifica si se recibió el cuerpo JSON y extrae la clave 'password'.
    2. **Validación de Lógica:** Compara la contraseña recibida con la contraseña predefinida.
    3. **Manejo de Resultado:**
       - Si es **incorrecta**, retorna un mensaje de error, pero con un estado **200** para
         indicar que el servidor procesó la solicitud exitosamente, pero el resultado
         de la validación es negativo.
       - Si es **correcta**, retorna un mensaje de éxito con un objeto `{'data': True}`.

    JSON Body esperado:
    {
      "password": "la_contraseña_a_validar"
    }

    Returns:
        Response: Un objeto de respuesta de Flask que indica si la contraseña es válida o no.
        
    Servira para validar todo tipo de servicios en los cuales se corre reisgo de manipular 
    mucha informacion, por eso se agrega esta funcionalidad.
    """
    try:
        claims = get_jwt()
        user_role = claims.get('role')  
        if user_role != 'comitiva':
            return send_error("No tienes permiso para validar la contrasenia", 403)
        
        request_data = request.json
        
        if not request_data:
            return send_error("No se recibieron datos", 400)
        print(f"Se recibieron los siguientes datos: {request_data}")
        
        data = {
            "password": request_data['password'],
            "manzana": claims.get('fraction'),
            "role": user_role,
            "name": claims.get('name')
        }
        #print([(data[dat], type(data[dat])) for dat in data])
        #Se debe verificar con la contrasenia que el propia del usuario
        #Se debe extraer la contrasenia y comprobar.
        #Se debe extraer el name y buscar la contrasenia en la base de datos.
        status, message, data = security_options.authenticate_user(data)        
        
        if status != 200:
            return send_error(message, status)
        
        return send_success("Validacion completa", {'data': True}, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)

@security_route.route('refresh_token/', methods=['POST'])
@jwt_required(refresh=True) # Usar el decorador correcto para refresh tokens
def refresh_token_fn() -> tuple[Any]:
    """
    Endpoint para generar un nuevo Access Token usando un Refresh Token.

    Esta ruta se utiliza para prolongar la sesión de un usuario sin obligarlo a
    reingresar sus credenciales.

    Restricción de Acceso:
    - Requiere un **Refresh Token** válido en el encabezado `Authorization` (debido al decorador `@jwt_required(refresh=True)`).

    Flujo de ejecución:
    1. **Extracción de Claims:** Utiliza `get_jwt_identity()` para obtener el ID del usuario (`current_user`)
       y `get_jwt()` para obtener todas las claims (`current_claims`) del token de refresco.
    2. **Validación de Claims:** Verifica que el claim 'service' exista en el token.
    3. **Generación de Nuevo Token:** Crea un **nuevo Access Token** utilizando:
       - El ID del usuario como `identity`.
       - Las claims existentes ('role', 'service', 'fraction') como `additional_claims`.
       *Nota: No genera un nuevo Refresh Token; solo el Access Token es actualizado.*
    4. **Respuesta:** Retorna el nuevo Access Token en una respuesta de éxito (200).

    JSON Body esperado:
    - El cuerpo JSON de la solicitud puede estar vacío (`{}`).

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que contiene el nuevo
                  `access_token` en el campo `data`.
    """
    try:
        # 1. Obtener el ID del usuario actual y las claims del refresh token
        current_user = get_jwt_identity()
        current_claims = get_jwt()  # Obtiene todas las claims del token actual
        service = current_claims.get('service')
        if not service:
            return send_error("No se encontro el servicio", 400)
            
        # 2. Crear un NUEVO access token (de corta duración) con las claims
        new_access_token = create_access_token(
            identity=current_user,
            additional_claims={
                "role": current_claims.get('role'),
                "service": current_claims.get('service'),
                "fraction": current_claims.get('fraction')
            }
        )
        return send_success("Token actualizado", {'data': new_access_token}, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
    
@security_route.route('admin_onwer/', methods=['POST'])
@role_required('delegado')
def get_onwer_info():
    """
    Endpoint principal de la API de administración de usuarios (Owners/Propietarios).
    
    Este endpoint está protegido y solo es accesible por usuarios con el rol **'delegado'**
    (@role_required('delegado')). Sirve como un punto de entrada unificado para dos
    funcionalidades críticas: la consulta de la lista de administradores y la creación de uno nuevo.

    El tipo de operación a realizar se determina examinando las claves en el cuerpo
    de la solicitud JSON (`request.json`):

    1.  **Consulta de Administradores (GET-like functionality):**
        - Se activa si el JSON contiene la clave **'get_onwers_info'** con un valor `True`.
        - Llama a `get_securyty_users_info()` para obtener la lista de todos los administradores
          registrados (limpiando campos sensibles como la contraseña).
        - Retorna un código 200/404.

    2.  **Creación de un Nuevo Administrador (POST functionality):**
        - Se activa si el JSON contiene la clave **'create_onwer'** con un diccionario anidado.
        - Llama a `security_options.insert_new_Onwer()`, la cual ejecuta el flujo transaccional
          completo: validación de elegibilidad del cliente, validación de unicidad de rol,
          validación de contraseña, y persistencia de datos.
        - Retorna códigos 201 (creación exitosa), 400 (error de validación de datos/contraseña),
          409 (conflicto de unicidad/elegibilidad), o 500 (error interno).

    Args:
        Ninguno explícito (recibe datos a través de `request.json` del framework).

    Returns:
        Response: Una respuesta HTTP (JSON) utilizando las funciones de utilidad `send_success` o
                  `send_error`, que contienen el código de estado, el mensaje y, opcionalmente, los datos.

    Excepciones manejadas:
        - `KeyError`: Si falta algún campo obligatorio esperado en el diccionario anidado. Retorna 400.
        - `Exception`: Cualquier otro error de ejecución no capturado. Retorna 500.
    """
    try:
        # Validar que se recibieron datos JSON en el cuerpo de la solicitud
        data_json = request.json
        if not data_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)

        print(f"Datos recibidos: {len(data_json)}")
        datos = None
        estado = None
        mensaje = None
        # Procesar solicitud de costo de servicio por año
        if 'get_onwers_info' in data_json and data_json['get_onwers_info']:
            datos = get_securyty_users_info() #Esta funcion va directamente la repositorio a traer la informacion de los usuarios
            if datos:
                estado = 200
                mensaje = "Datos obtenidos correctamente"
            else:
                estado = 404
                mensaje = "No se encontraron datos"

        if 'create_onwer' in data_json and data_json['create_onwer']:
            estado, mensaje = security_options.insert_new_Onwer(data_json['create_onwer'])
            print(f"Datos recibidos: {datos}")
        

        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
        else:
            return send_error(mensaje, estado)
                
    except KeyError as e:
        error_msg = f"Campo obligatorio faltante en los datos: {e}"
        print(f"Error de validación: {error_msg}")
        return send_error(error_msg, 400)
    except Exception as e:
        error_msg = f"Error interno al procesar la solicitud: {e}"
        print(f"Error al obtener el costo: {error_msg}")
        return send_error(error_msg, 500)
        



@security_route.route('validate_password/', methods=['POST'])
@jwt_required()
def check_admin_password() -> tuple[Any]:
    """
    Endpoint para validar una contraseña de forma aislada.

    Este endpoint se utiliza para verificar una contraseña específica (hardcodeada
    como 'qwerty' en la lógica actual) para una funcionalidad secundaria, como
    una doble verificación de seguridad antes de una acción crítica (ej. un corte de caja).

    Restricción de Acceso:
    - Solo usuarios con el rol **'comitiva'** pueden acceder a esta ruta (debido al decorador `@role_required('comitiva')`).

    Flujo de ejecución:
    1. **Validación de Datos:** Verifica si se recibió el cuerpo JSON y extrae la clave 'password'.
    2. **Validación de Lógica:** Compara la contraseña recibida con la contraseña predefinida.
    3. **Manejo de Resultado:**
       - Si es **incorrecta**, retorna un mensaje de error, pero con un estado **200** para
         indicar que el servidor procesó la solicitud exitosamente, pero el resultado
         de la validación es negativo.
       - Si es **correcta**, retorna un mensaje de éxito con un objeto `{'data': True}`.

    JSON Body esperado:
    {
      "password": "la_contraseña_a_validar"
    }

    Returns:
        Response: Un objeto de respuesta de Flask que indica si la contraseña es válida o no.
        Esta sera exclusiva del delegado para que el escriba su contrasenia y se valida si es correcta
        Se debe temrinar de implementar este endpoint para toda la parte de validaciones de comitiva
    """
    try:
        claims = get_jwt()
        user_role = claims.get('role')  
        if user_role != 'comitiva':
            return send_error("No tienes permiso para validar la contrasenia", 403)
        
        request_data = request.json
        
        if not request_data:
            return send_error("No se recibieron datos", 400)
        #print(f"Se recibieron los siguientes datos: {request_data}")
        
        #print([(data[dat], type(data[dat])) for dat in data])
        #Se debe verificar con la contrasenia que el propia del usuario
        #Se debe extraer la contrasenia y comprobar.
        #Se debe extraer el name y buscar la contrasenia en la base de datos.
        status, message = security_options.validate_admin_password(request_data['password'])        
        
        if status != 200:
            return send_error(message, status)
        
        return send_success("Validacion completa", {'data': True}, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
