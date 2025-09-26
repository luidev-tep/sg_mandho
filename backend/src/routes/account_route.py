# Blueprint del usuario, se hace para separar el codigo y dejar app.py limpio

from typing import Literal
from flask import Blueprint, request
from flask.wrappers import Response
from typing import Any
from src.accounts.account import AccountCrud

from src.routes.handle_message import send_error, send_success

#Importaciones para crear cuenta

account_options = AccountCrud()
account_route = Blueprint('account_route', __name__, url_prefix='/api/account/')
from src.security.security import role_required

from flask_jwt_extended import jwt_required,  get_jwt, get_jwt_identity


@account_route.route('create/', methods=['POST'])
@jwt_required()
def crate_account() -> tuple[Response, Literal[400]] | tuple[Response, Any] | tuple[Response, Literal[500]]:
    """
    Endpoint para crear una nueva cuenta de cliente.

    Este endpoint recibe los datos necesarios para crear una nueva cuenta a través
    de una solicitud POST en formato JSON.

    Restricción de Acceso:
    - Requiere autenticación JWT (`@jwt_required`).
    - Solo los usuarios con el rol **'delegado'** o **'subdelegado'** están autorizados
      para crear cuentas.

    Flujo de ejecución interno:
    1. **Autorización:** Extrae el rol del usuario de las claims del JWT. Si el rol no
       es 'delegado' o 'subdelegado', retorna un error 403 (Prohibido).
    2. **Validación de Datos:** Verifica que el cuerpo de la solicitud JSON no esté vacío.
    3. **Lógica de Negocio:** Llama a `account_options.insert_account(account_json)` para
       procesar la creación de la cuenta. Esta función de la capa de negocio se encarga de
       la inserción en la base de datos.
    4. **Respuesta:**
       - Si la operación de inserción es exitosa (estado 200 a 205), retorna un mensaje
         de éxito.
       - Si la inserción falla por cualquier motivo (ej. datos incorrectos), retorna un
         mensaje de error con el estado correspondiente.
    5. **Manejo de Excepciones:** Si ocurre un error inesperado, captura la excepción
       y retorna un error 500 (Error Interno del Servidor).

    JSON Body esperado (ejemplo):
    {
        "person_id": "str",      // El ID de la persona a la que se le asociará la cuenta.
        "account_type": "str",   // Tipo de cuenta (ej. "agua", "luz").
        // ... otros datos relevantes para la cuenta.
    }

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que indica el resultado de la
                  operación.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'subdelegado':
        pass
    else:
        return send_error("No tienes permiso para crear cuentas", 403)
    try:
        account_json = request.json

        if not account_json:
                return send_error("No se recibieron datos", 400)

        estado, mensaje = account_options.insert_account(account_json)
        
        if 200 <= estado <= 205:
            return send_success(mensaje,None, estado)
        else:
            return send_error(mensaje, estado)
    except Exception as e:
        print(f"Error al crear la cuenta: {e}")
        return send_error(str(e), 500)


@account_route.route('read/', methods=['POST'])
@jwt_required()
def read_account() -> tuple[Response, Literal[400]] | tuple[Response, int] | tuple[Response, Literal[500]] | None:
    """
    Endpoint para leer información de una o varias cuentas.

    Este endpoint tiene dos modos de operación, determinados por el contenido del
    cuerpo de la solicitud JSON:
    - **Lectura específica:** Si el JSON contiene un `account_id` u otro filtro
      específico, se retorna la información de esa única cuenta.
    - **Lectura masiva:** Si el JSON está vacío, se retorna la información de
      todas las cuentas.

    Restricción de Acceso:
    - Requiere autenticación JWT (`@jwt_required`).
    - Solo usuarios con el rol **'delegado'**, **'subdelegado'** o **'comitiva'**
      pueden acceder a esta ruta.

    Flujo de ejecución interno:
    1. **Autorización:** Extrae el rol del usuario del JWT y verifica si está autorizado.
    2. **Validación de Datos:** Verifica que se haya recibido un cuerpo JSON.
    3. **Lógica de Negocio:** Llama a `account_options.read_account(account_json)`
       para ejecutar la consulta a la base de datos.
    4. **Respuesta:** Retorna una respuesta de éxito con los datos encontrados o una
       respuesta de error si la búsqueda falla.
    5. **Manejo de Excepciones:** Captura cualquier excepción y retorna un error 500.

    JSON Body esperado (ejemplo):
    - Para buscar una cuenta específica:
      { "account_id": "12345abcde" }
    - Para buscar todas las cuentas:
      { }

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que contiene los datos
                  de la(s) cuenta(s) en caso de éxito o un mensaje de error si
                  la solicitud no cumple con los requisitos o falla.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'subdelegado' or user_role == 'comitiva':
        pass
    else:
        return send_error("No tienes permiso para crear cuentas", 403)
    try:
        
        account_json = request.json
        if not account_json:
            return send_error("No se recibieron datos", 400)
        
        estado, mensaje, datos = account_options.read_account(account_json)
        if 200 <= estado <= 205:
            #print(datos)
            return send_success(mensaje,datos, estado)
        else:
            return send_error(mensaje, estado)
    except Exception as e:
        print(f"Error al crear la cuenta: {e}")
        return send_error(str(e), 500)