# Blueprint del usuario, se hace para separar el codigo y dejar app.py limpio
from typing import Literal, Any
from flask import Blueprint, request

from src.users.user import UserCrud, get_home_info

user_options = UserCrud()

#Traer mensje de error dinamicos 
from src.routes.handle_message import send_error, send_success

home_route = Blueprint('home_route', __name__, url_prefix='/api/home') 

from flask_jwt_extended import jwt_required,  get_jwt

@home_route.route("/get_home_info", methods=["GET"]) 
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
    user_role = claims.get('role', '')
    
    if user_role == 'delegado' or user_role == 'comitiva'  or user_role == 'subdelegado':
        pass
    else:
        return send_error("No tienes permiso para ver esta informacion", 403)
    try:
        state, message, data = get_home_info()

        if 200 <= state <= 205:
            
            return send_success(message, data, 200)
        else:
            return send_error(message, state)
        
    except Exception as e:
        print(e, "error desde read users")
        return send_error(str(e), 500)
   