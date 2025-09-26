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

security_route = Blueprint('security_route', __name__, url_prefix='/api/security/')

# 1. Obtener información de la URL como PARÁMETROS DE RUTA
#    Ejemplo de URL: /api/auth/read_user/123 (donde 123 es el user_id)
# 1. Obtener información de la URL como PARÁMETROS DE RUTA
#    Ejemplo de URL: /api/auth/read_user/123 (donde 123 es el user_id)
@security_route.route('login/', methods=['POST'])
def login() -> tuple[Any]:# -> tuple[Response, Literal[404]] | Any | tuple[Response, Lit...:
    """
    Obtiene la información de un usuario específico por su ID de la URL.

    Args:
        user_id (int): El ID del usuario a buscar, extraído de la URL.

    Returns:
        dict: Información del usuario.

    Por el momento esta funcion aun no se implementara sin embargo, se mandaran los datos del ususario que funga como administrador
    y se retornara un mensaje de que se obtuvo la informacion correctamente.
    ESTA FUNCION ES SOLAMENTE DE TESTEO YA QUE NO RESPETA LA SEGURIDAD Y LA LOGICA IMPLEMENTADA ES SOLO PARA UNA 
    PARTE DEL NEGOCIO SE DEBE MOFICIAR DESPUES
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
            "fraction": user_data['CustomerFraction']
                        }
            )
        refresh_token = create_refresh_token(
            identity=user_data['DIM_ServiceOwnersId'],
            additional_claims={
            "role": user_data['RoleName'],
            "service": user_data['ServiceName'],
            "fraction": user_data['CustomerFraction']
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


@security_route.route('validate_password/', methods=['POST'])
@role_required('comitiva')
def validar_password() -> tuple[Any]:
    """
    Endpoint para validar una contraseña.

    Esta función actúa como una barrera de seguridad, verificando si la contraseña
    proporcionada en la solicitud POST coincide con la contraseña predefinida.
    
    Returns:
        tuple[Any]: Una tupla que contiene la respuesta HTTP. Si la contraseña es
                    correcta, devuelve un mensaje de éxito. Si es incorrecta,
                    devuelve un mensaje de error con un código de estado 200 para
                    indicar una respuesta válida del servidor. En caso de error
                    interno o datos faltantes, devuelve un mensaje de error apropiado.
    
    HTTP Methods:
        POST: Se utiliza para enviar la contraseña a validar en el cuerpo de la solicitud JSON.
              El cuerpo de la solicitud debe ser un JSON con la clave 'password'.
              Ejemplo:
              {
                "password": "la_contraseña_a_validar"
              }
    """
    try:
        request_data = request.json
        if not request_data:
            return send_error("No se recibieron datos", 400)
        
        password = 'qwerty' 

        isValid = request_data['password'] == password

        if not isValid:
            return send_error("La contrasenia es incorrecta, intentelo de nuevo", 200)
        
        return send_success("Validacion completa", {'data': True}, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
    


@security_route.route('refresh_token/', methods=['POST'])
@jwt_required(refresh=True) # Usar el decorador correcto para refresh tokens
def refresh_token_fn() -> tuple[Any]:
    try:
        print(f"Se refresco el token ")
        # 1. Obtener el ID del usuario actual y las claims del refresh token
        current_user = get_jwt_identity()
        current_claims = get_jwt()  # Obtiene todas las claims del token actual
        
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

