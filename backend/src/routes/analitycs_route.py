from flask import Blueprint, Response, request
from typing import Any, Literal

from src.routes.handle_message import send_error, send_success
from src.payments.payment import PaymentCrud
from src.analytics_reports.Analitycs import Analitycs

# Instancias de las clases de negocio y repositorio
handler_analythics = Analitycs()
payment_options = PaymentCrud()

# Creación de un Blueprint para las rutas de analíticas
analitycs_route = Blueprint('analitycs_route', __name__, url_prefix='/api/analitycs/')

from flask_jwt_extended import jwt_required,  get_jwt


@analitycs_route.route('get_analytics/', methods=['POST'])
@jwt_required()
def get_analythics_by_service() -> tuple[Response, Literal[404]] | Any | tuple[Response,Literal[500]] | tuple[Response, Literal[200]]:
    """
    Endpoint para obtener datos de analíticas filtradas por servicio/comitiva, mes y año.

    Recibe filtros específicos en el cuerpo JSON de una petición POST para consultar
    datos analíticos (ej. reportes mensuales, desempeño de un servicio).

    Restricción de Acceso:
    - Requiere autenticación JWT (`@jwt_required`).
    - Solo usuarios con el rol **'delegado'** o **'comitiva'** están autorizados para acceder a esta ruta.

    Flujo de ejecución interno:
    1. **Autorización:** Extrae el rol del usuario de las claims del JWT. Si el rol no es
       'delegado' o 'comitiva', retorna un error 403 (Prohibido).
    2. **Validación de Datos:** Verifica que el cuerpo de la solicitud JSON no esté vacío.
    3. **Lógica de Negocio:** Llama a `handler_analythics.get_analytics_per_month(data)` para
       ejecutar la consulta. Esta función retorna el estado HTTP, un mensaje y los datos.
    4. **Respuesta:**
       - Si el estado de la lógica de negocio es de éxito (200 a 205), retorna el resultado
         con `send_success`.
       - Si el estado es de error, retorna el mensaje de error con `send_error`.
    5. **Manejo de Excepciones:** Captura cualquier error inesperado y retorna un error 500
       (Error Interno del Servidor).

    JSON Body esperado:
    {
        "comitiva": "str",      // Nombre o identificador del servicio/comitiva a consultar.
        "mes": "str",           // Mes para el filtro (ej. "M01" para enero).
        "usuario": "str",       // UUID del usuario (posiblemente para restringir o auditar).
        "anio": "str"           // Año para el filtro (ej. "Y25" para 2025).
    }

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que indica el resultado:
                  - 200/205 (Éxito) y los datos de las analíticas.
                  - 400 (Datos faltantes).
                  - 403 (Permiso denegado por rol).
                  - 500 (Error interno).
    """
    claims = get_jwt()
    user_role = claims.get('role')
    if user_role == 'delegado' or user_role == 'comitiva':
        pass
    else:
        return send_error("No tienes permiso para buscar", 403)
    try:
        data = request.json

        # Valida que se hayan recibido datos en el cuerpo de la petición
        if not data:
            return send_error("No se recibieron datos", 400)
        
        # Llama a la función de la capa de negocio para obtener las analíticas
        estado, mensaje, datos = handler_analythics.get_analytics_per_month(data)

        # Retorna una respuesta exitosa o de error basada en el estado devuelto
        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
        else:
            return send_error(mensaje, estado)
        
    except Exception as e:
        # Manejo de errores inesperados del servidor
        print(f"Error al obtener la informacion de la comitiva: {e}")
        return send_error(f"Error al procesar la solicitud: {str(e)}", 500)