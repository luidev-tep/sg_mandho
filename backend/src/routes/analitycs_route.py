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

@analitycs_route.route('get_analytics/', methods=['POST'])
def get_analythics_by_service() -> tuple[Response, Literal[404]] | Any | tuple[Response,Literal[500]] | tuple[Response, Literal[200]]:
    """
    Endpoint para obtener datos de analíticas por comitiva.

    Recibe un JSON con los filtros de búsqueda a través de una petición POST.
    Valida los datos y, si son correctos, invoca la lógica de negocio para
    recopilar y devolver las analíticas correspondientes al servicio.

    Se espera un JSON con la siguiente estructura:
    {
        "comitiva": "agua", 
        "mes": "M01", 
        "usuario": "uuid_del_usuario",
        "anio": "Y25"
    }

    Returns:
        Union[tuple[Response, int], Any]:
            - Una tupla con un objeto Response y un código de estado HTTP 400
              si los datos son incorrectos.
            - Una tupla con un objeto Response y un código de estado HTTP 200
              si la operación es exitosa, incluyendo los datos de las analíticas.
            - Una tupla con un objeto Response y un código de estado HTTP 500
              en caso de un error interno del servidor.
    """
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