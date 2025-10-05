# Blueprint del usuario, se hace para separar el codigo y dejar app.py limpio

from typing import Literal
from flask import Blueprint, Response, request, jsonify
from src.users.user import UserCrud
from src.dim_dates.dim_date import DIM_DATE
from src.utils.conexion import Conexion  # Usa tu clase de conexión existente


from src.routes.handle_message import send_error

personas = UserCrud()

search_route = Blueprint('search_route', __name__,url_prefix='/api/search/')

from flask_jwt_extended import jwt_required,  get_jwt, get_jwt_identity
#Recordar poner el / si es que los enpoins dan error
@search_route.route("search_client/", methods=["GET"])
@jwt_required()
def busqueda_tiempo_real() -> tuple[Response, Literal[400]] | Response | tuple[Response, Literal[500]]:
    """
    Endpoint para búsqueda en tiempo real de clientes/usuarios.
    
    Realiza una búsqueda case-insensitive en múltiples campos de los usuarios y devuelve
    resultados coincidentes en formato estandarizado.
    
    Parámetros GET:
    ---------------
    q : str
        Término de búsqueda (mínimo 3 caracteres). Se busca en:
        - first_name
        - second_name
        - last_name
        - id_user
        - manzana
    
    Respuestas:
    ----------
    200 - Éxito:
        {
            "status": "success",
            "count": int,
            "results": [
                {
                    "id": str,               # ID único del usuario
                    "text": str,             # Nombre formateado
                    "data": dict,            # Datos completos del usuario
                    "selectable": bool,       # Siempre True en esta implementación
                    "reason": str            # Siempre vacío en esta implementación
                },
                ...
            ]
        }
    
    400 - Búsqueda inválida (menos de 3 caracteres):
        {
            "results": [],
            "message": "Ingrese mínimo 3 caracteres"
        }
    
    500 - Error del servidor:
        {
            "status": "error",
            "message": str  # Descripción del error
        }
    
    Ejemplo de uso:
    --------------
    GET /api/account/search_client?q=torres
    
    Ejemplo de respuesta exitosa:
    {
        "status": "success",
        "count": 2,
        "results": [
            {
                "id": "JUA-LON-CERR-322h2fwiu",
                "text": "John",
                "data": {
                    "date_id": "---q3ri3guyefceudx",
                    "id_user": "JUA-LON-CERR-322h2fwiu",
                    "first_name": "John",
                    ...
                },
                "selectable": true,
                "reason": ""
            }
        ]
    }
    """
    # 1️⃣ Validar rol del usuario
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role not in ['delegado', 'subdelegado', 'comitiva']:
        return send_error("No tienes permiso para buscar", 403)

    # 2️⃣ Validar parámetro de búsqueda
    search_term = request.args.get('q', '').strip().lower()
    if not search_term or len(search_term) < 3:
        return jsonify({
            'results': [],
            'message': 'Ingrese mínimo 3 caracteres'
        }), 400

    handler_date = DIM_DATE()
    conn = None
    try:
        # 3️⃣ Conexión a BD
        db_handler = Conexion()
        conn, cursor = db_handler.conexion()

        # 4️⃣ Consulta SQL con filtro directo (LIKE)
        # Nota: El uso de parámetros evita inyección SQL
        like_term = f"%{search_term}%"
        query = """
        SELECT 
            DIM_CustomerId,
            DIM_DateId,
            CustomerName,
            CustomerMiddleName,
            CustomerLastName,
            CustomerSecondLastName,
            CustomerDateBirth,
            CustomerStartDate,
            CustomerEndDate,
            CustomerAddress,
            CustomerFraction,
            CustomerNumberExt
        FROM DIM_Customer
        WHERE LOWER(CustomerName) LIKE ?
           OR LOWER(CustomerMiddleName) LIKE ?
           OR LOWER(CustomerLastName) LIKE ?
           OR LOWER(CustomerSecondLastName) LIKE ?
           OR CustomerFraction LIKE ?
        LIMIT 50;
        """
        cursor.execute(query, (like_term, like_term, like_term, like_term, like_term))
        registros = cursor.fetchall()

        # 5️⃣ Mapear registros a formato del frontend
        #Se puede agregar toda la logica para filtra por personas muertas 
        #y poner a persons inactivas en amarillo
        resultados = []
        for r in registros:
            registro = {
                "id_user": r[0],
                "date_id": r[1],
                "first_name": r[2],
                "second_name": r[3],
                "last_name": r[4],
                "second_last_name": r[5],
                "date_of_birth": r[6],
                "date_user_start": r[7],
                "date_user_end": r[8],
                "manzana": r[9],
                "street": r[10],
                "number_ext": r[11],
            }

            registro['edad'] = handler_date.get_age(registro.get('date_of_birth'))
            
            #Se agreggo el registro con el que se filtran directamente a las personas muertas.
            if r[8] == 's/n':
                resultados.append({
                    "id": registro["id_user"],
                    "text": registro["first_name"],
                    "data": registro,
                    "selectable": True,
                    "reason": ""
                })

        # 6️⃣ Retornar respuesta
        return jsonify({
            "status": "success",
            "count": len(resultados),
            "results": resultados
        })

    except Exception as e:
        print(f"Error en búsqueda optimizada: {str(e)}")
        return send_error(str(e), 500)

    finally:
        if conn:
            conn.close()