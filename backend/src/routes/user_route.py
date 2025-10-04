# Blueprint del usuario, se hace para separar el codigo y dejar app.py limpio
from typing import Literal, Any
from flask import Blueprint, request

from src.users.user import UserCrud

user_options = UserCrud()

#Traer mensje de error dinamicos 
from src.routes.handle_message import send_error, send_success

user_route = Blueprint('user_route', __name__)

from flask_jwt_extended import jwt_required,  get_jwt

@user_route.route('/api/user/create_user/', methods=['POST'])
@jwt_required()
def create_user():# -> tuple[Any, Literal[400]] | tuple | tuple[Any, Literal[500]]:
    """
    Endpoint para crear un nuevo usuario.

    Este endpoint se encarga de la creación de un nuevo usuario a partir de los datos
    recibidos en el cuerpo de una solicitud POST. Requiere autenticación JWT.
    La creación está restringida a usuarios con los roles 'delegado' o 'subdelegado'.

    - Si el rol es 'subdelegado', se valida que el usuario esté creando a alguien
      en su misma "fracción" (manzana) para mantener la seguridad y el control de acceso.
    - Delega la lógica de negocio a la función `user_options.insert_user`.

    JSON Body esperado:
    {
      "data": {
        "manzana": "str", // La fracción o manzana del usuario a crear
        // ... otros campos del usuario
      }
    }

    Returns:
        Response: Un objeto de respuesta de Flask que contiene un JSON con el
                  estado de la operación, un mensaje y los datos de la respuesta.
                  - Éxito: Retorna un JSON con el ID del usuario creado.
                  - Error: Retorna un JSON con el mensaje de error y el estado HTTP.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    user_fraction = claims.get('fraction', '').strip().lower()
    request_data = request.json

    # print(f"------IMPRIMIENTO INFORMACION DEBUG------")
    # print(f"Rol del usuario: {user_role}")
    # print(f"Fraccion del usuario: {user_fraction}")
    # print(f"Datos recibidos en la solicitud: {request_data}")
    if not request_data:
        return send_error("No se recibieron datos", 400)
    
        # Extraemos los filtros de la solicitud. Si no existen, usamos un diccionario vacío.
    data = request_data.get('data', {})
    
    customerfraction = data.get('manzana', '').strip().lower()

    if user_role == 'delegado':
        pass
    elif user_role == 'subdelegado':
        # Forzamos que el filtro de fracción sea el del subdelegado para seguridad.
        
        if customerfraction != user_fraction:
            return send_error(f"No tienes permiso para crear usuarios en {customerfraction}", 403)
    else:
        return send_error("No tienes permiso para registrar usuarios", 403)
    try:
        
        estado, mensaje, persona_id = user_options.insert_user(request_data['data'])
        
        if 200 <= estado <= 205:
            data = {
                "id": persona_id,
                }
            print(mensaje)
            return send_success(mensaje, data,estado)
        else:
            print(mensaje)
            return send_error(mensaje, estado)
        
    except Exception as e:
        print(e)
        return send_error(str(e), 500)


@user_route.route("/api/user/read_user/", methods=["POST"])  # Sin slash
@jwt_required()
def read_information() -> tuple[Any, Literal[400]] | tuple[Any, Literal[200]] | tuple | tuple[Any, Literal[500]]:
    """
    Endpoint para la lectura de información de usuarios con filtros.

    Permite obtener la información de uno o varios usuarios. El cuerpo de la solicitud
    debe incluir un ID de usuario o un diccionario de filtros para la búsqueda.
    Los campos 'id_user' y 'filters' son mutuamente excluyentes.

    Las restricciones de acceso se aplican de la siguiente manera:
    - Usuarios 'delegado' y 'comitiva' tienen acceso a la información completa.
    - Usuarios 'subdelegado' solo pueden consultar usuarios de su misma "fracción".

    JSON Body esperado:
    {
      "id_user": "str", // ID del usuario, si se quiere buscar a uno en específico.
      "filters": {
          "CustomerFraction": "str", // La fracción a la que pertenece el usuario
          // ... otros campos para filtrar
      }
    }

    Returns:
        Response: Un objeto de respuesta de Flask con un JSON que contiene los datos
                  solicitados en caso de éxito o un mensaje de error si la
                  solicitud no cumple con los requisitos o falla.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    user_fraction = claims.get('fraction', '').strip().lower()
    request_data = request.json
    
    # print(f"------IMPRIMIENTO INFORMACION DEBUG------")
    # print(f"Rol del usuario: {user_role}")
    # print(f"Fraccion del usuario: {user_fraction}")
    # print(f"Datos recibidos en la solicitud: {request_data}")
    if not request_data:
        return send_error("No se recibieron datos", 400)

    # Extraemos los filtros de la solicitud. Si no existen, usamos un diccionario vacío.
    filters = request_data.get('filters', {})

    if user_role == 'delegado' or user_role == 'comitiva':
        pass
    elif user_role == 'subdelegado':
        # Forzamos que el filtro de fracción sea el del subdelegado para seguridad.
        filters['CustomerFraction'] = [user_fraction]
        # Actualizamos los filtros en el objeto de la solicitud que se pasará a la lógica de negocio.
        request_data['filters'] = filters
    else:
        return send_error("No tienes permiso para ver esta informacion", 403)
    try:
        state, message, data = user_options.read_user(request_data)

        if 200 <= state <= 206:
            
            return send_success(message, data, 200)
        else:
            return send_error(message, state)
        
    except Exception as e:
        print(e, "error desde read users")
        return send_error(str(e), 500)
    

@user_route.route("/api/user/update_user/", methods=["POST"])
@jwt_required()
def update_info_user() -> tuple[Any]:
    """
    Endpoint para actualizar la información de un usuario.

    Este endpoint espera recibir los datos a actualizar en formato JSON a través
    de una solicitud POST. Requiere autenticación JWT y que el usuario tenga
    el rol 'delegado' o 'subdelegado'.

    - Delega la lógica de actualización a la función `user_options.edit_user`.
    - Retorna una respuesta de éxito si la operación fue exitosa, o un mensaje
      de error con el estado HTTP correspondiente en caso de fallo.

    JSON Body esperado:
    {
      "id_user": "str", // ID del usuario a actualizar.
      "data": {
        "nombre": "nuevo_nombre",
        // ... otros campos a modificar
      }
    }

    Returns:
        Response: Un objeto de respuesta de Flask con el resultado de la operación.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'subdelegado':
        pass
    else:
        return send_error("No tienes permiso para editar a un usuario", 403)
    try:
        request_data = request.json
        if not request_data:
            return send_error("No se recibieron datos", 400)
        
        state, message, data = user_options.edit_user(request_data)

        if 200 <= state <= 206:
            return send_success(message, data, state)
        else:
            print(message)
            return send_error(message, state)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
    

@user_route.route("/api/user/delete_user/", methods=["PATCH"])
@jwt_required()
def userDefuncion() -> tuple[Any, Literal[400]] | tuple | tuple[Any, Literal[500]]:
    """
    Endpoint para manejar la "defunción" de un usuario.

    Este endpoint, utilizando el método PATCH, permite actualizar un registro de usuario
    para marcarlo como "fallecido", lo que podría incluir el registro de una fecha
    de defunción. Requiere autenticación JWT y que el usuario tenga el rol 'delegado' o 'subdelegado'.
    Delega la lógica principal a la función `user_options.defuncion_user`.

    JSON Body esperado:
    {
      "id_user": "str", // ID del usuario a marcar como fallecido
    }

    Returns:
        Response: Un objeto de respuesta de Flask con el resultado de la operación,
                  incluyendo el registro del usuario modificado.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'subdelegado':
        pass
    else:
        return send_error("No tienes permiso para eliminar a un usuario", 403)
    try:
        defuncion_data = request.json
        if not defuncion_data:
            return send_error("No se recibieron datos", 400)
        
        state, message, data = user_options.defuncion_user(defuncion_data)

        if 201 == state :
            print(f"El estado {state}  Mensaje: {message}, la informacion {data}")
            return send_success(message, data, state)
        else:
            print(message)
            return send_error(message, state)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)


@user_route.route("/api/user/gat_data/", methods=["GET"])
@jwt_required()
def get_data_customer_payments() -> tuple[dict, int]:
    """
    Endpoint para obtener datos de pagos de un cliente específico.

    Este endpoint permite obtener la información de los pagos asociados a un cliente
    dado su ID. Se realiza a través de una solicitud GET.
    Requiere autenticación JWT y es accesible para los roles 'delegado', 'subdelegado'
    y 'comitiva'.

    Parámetros de la URL (Query Parameters):
    - Dim_customerId: El ID del cliente del cual se desean obtener los datos.

    Returns:
        Response: Un objeto de respuesta de Flask con los datos del cliente y sus pagos
                  en caso de éxito, o un mensaje de error si el ID del cliente no
                  fue proporcionado o si la búsqueda falla.
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'subdelegado' or user_role == 'comitiva':
        pass
    else:
        return send_error("No tienes permiso para obtener datos de un usuario", 403)
    try:
        dim_customer_id = request.args.get('Dim_customerId')
        
        if not dim_customer_id:
            return send_error("No se recibió el ID del cliente", 400)
        #print('Antes de la logica principal')
        state, message, data = user_options.get_data_customer_payments(dim_customer_id)
        #print('Sale de la logica principal')
        if state == 200:
            print(f"Estado: {state}, Mensaje: {message}")
            return send_success(message, data, state)
        else:
            print(f"Error: {message}")
            return send_error(message, state)
    except Exception as e:
        print(f"Excepción: {e}")
        return send_error(str(e), 500)
    
    