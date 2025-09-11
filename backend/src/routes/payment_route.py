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
        
        estado, mensaje, datos = payment_options.create_payment(payment_json)

        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
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
            
        if 'filters' in payment_json:
            estado, mensaje, datos = payment_options.read_payments(payment_json)

            if 200 <= estado <= 205:
                return send_success(mensaje, datos, estado)
            else:
                return send_error(mensaje, estado)
            
        if "DIM_CustomerId" in payment_json:

            estado, mensaje, datos = payment_options.read_payments_customer_id(payment_json)
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
            serviceName: str, "Nombre del servicio o producto"
            DIM_CustomerId: str, "ID del cliente"
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
    


@payment_route.route('get_any_data/', methods=['POST'])
def get_any_data() -> Response:
    """
    Endpoint para obtener datos diversos del sistema que no requieren procesamiento complejo.
    
    Esta función actúa como un punto de entrada genérico para consultas simples donde el backend
    necesita recibir una petición específica pero el procesamiento es mínimo. Es útil para obtener
    información auxiliar, configuraciones simples o datos de referencia que no justifican endpoints
    dedicados.
    
    Flujo de ejecución:
    1. Recibe y valida los datos JSON de la solicitud
    2. Interpreta el tipo de consulta basado en los campos recibidos
    3. Ejecuta la función correspondiente según el tipo de dato solicitado
    4. Retorna la respuesta apropiada con el formato estándar de la API
    
    Parámetros esperados en el JSON:
    - costoservicio: Dict con información para consultar costos por año de pago
        Ejemplo: {"costoservicio": {"year": 2023, "service_type": "premium"}}
    
    Códigos de respuesta:
    - 200: Éxito en la operación
    - 400: Datos faltantes o formato incorrecto
    - 500: Error interno del servidor
    
    Nota: Este endpoint está diseñado para ser extendido con nuevos tipos de consultas
    agregando más condiciones 'if' según se necesiten nuevos servicios.
    
    Returns:
        Response: Objeto de respuesta Flask con el formato JSON estándar de la API
    """
    try:
        # Validar que se recibieron datos JSON en el cuerpo de la solicitud
        data_json = request.json
        if not data_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)

        #print(f"Datos recibidos: {data_json}")

        # Procesar solicitud de costo de servicio por año
        if 'costoservicio' in data_json and data_json['costoservicio']:
            estado, mensaje, datos = payment_options.get_cost_by_payment_year(data_json['costoservicio'])
        
        # Aquí se pueden agregar más condiciones para otros tipos de servicios en el futuro
        # Ejemplo:
        # elif 'otro_servicio' in data_json:
        #     estado, mensaje, datos = otra_funcion(data_json['otro_servicio'])
        
        # Validar y retornar respuesta según el estado recibido
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