from flask import Blueprint, request, Response
from src.routes.handle_message import send_error, send_success

# importacion del manejo de pagos
from src.payments.payment import PaymentCrud

payment_options = PaymentCrud()

payment_route = Blueprint('payment_route', __name__, url_prefix='/api/payment/')

@payment_route.route('create/', methods=['POST'])
def create_payment() -> Response:
    """
    Maneja la creación de un nuevo pago a través de una solicitud POST.

    Este endpoint recibe los datos de un pago en formato JSON, los valida y
    los procesa a través de la lógica de negocio de la clase `PaymentCrud`.
    Devuelve una respuesta JSON con el estado de la operación.

    Returns:
        Response: Un objeto de respuesta de Flask que contiene un JSON con el
                  estado HTTP y un mensaje de éxito o error.
    """
    try:
        payment_json = request.json
        if not payment_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        estado, mensaje = payment_options.create_payment(payment_json)

        if 200 <= estado <= 205:
            return send_success(mensaje, None, estado)
        else:
            return send_error(mensaje, estado)
            
    except Exception as e:
        print(f"Error al crear el pago: {e}")
        return send_error(str(e), 500)
    

@payment_route.route('read/', methods=['POST'])
def read_payment() -> Response:
    """
    Maneja la lectura de un pago a través de una solicitud POST.

    Este endpoint recibe los datos necesarios para identificar los pagos
    devuelve la información del pago correspondiente.

    Ya que servira, para obtenenr un solo pago, obtener todos los pagos o
    filtrar los pagos por ciertos criterios.

    Args:{
            filters: dict, "filtros para la busqueda de la informacion de la persona" 
            //Este endpoind sera solo para la infromacion en general puesto que deben haver algunos filtros especificos 
        }
    Returns:
        Response: Un objeto de respuesta de Flask que contiene un JSON con
                  el estado HTTP y los datos del pago o un mensaje de error.
    """
    try:
        payment_json = request.json
        if not payment_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        estado, mensaje, datos = payment_options.read_payments(payment_json)

        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
        else:
            return send_error(mensaje, estado)
            
    except Exception as e:
        print(f"Error al leer el pago: {e}")
        return send_error(str(e), 500)
    
#get_cost
@payment_route.route('get_cost/', methods=['POST'])
def get_cost() -> Response:
    """
    Maneja la obtención del costo de un servicio o producto a través de una solicitud POST.

    Este endpoint recibe los datos necesarios para calcular el costo y
    devuelve el costo correspondiente.

    Args:{
            service_id: int, "ID del servicio o producto"
            quantity: int, "Cantidad del servicio o producto"
            //Este endpoind sera solo para la infromacion en general puesto que deben haver algunos filtros especificos 
        }
    Returns:
        Response: Un objeto de respuesta de Flask que contiene un JSON con
                  el estado HTTP y el costo calculado o un mensaje de error.
    """
    try:
        cost_json = request.json
        if not cost_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        estado, mensaje, datos = payment_options.get_cost(cost_json)

        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
        else:
            return send_error(mensaje, estado)
            
    except Exception as e:
        print(f"Error al obtener el costo: {e}")
        return send_error(str(e), 500)