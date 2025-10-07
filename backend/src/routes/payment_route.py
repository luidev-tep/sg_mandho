"""
Módulo: payment_route.py
Descripción:
    Define las rutas (Blueprints) para las operaciones relacionadas con la gestión
    de pagos, costos de servicios y cortes de caja dentro de la API.
    Utiliza Flask, JWT para seguridad y clases CRUD para la lógica de negocio.
"""

from flask import Blueprint, request, Response
from src.routes.handle_message import send_error, send_success

# importacion del manejo de pagos
from src.payments.payment import PaymentCrud

payment_options = PaymentCrud()

from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud

from src.payments.cash_cut import cashCutCrud
from src.security.security import SecurityUsers, role_required

from flask_jwt_extended import jwt_required,  get_jwt
service_details_options = ServiceDetailsCrud()

hanlder_cash_cut = cashCutCrud()

security_options = SecurityUsers()

payment_route = Blueprint('payment_route', __name__, url_prefix='/api/payment/')


@payment_route.route('create/', methods=['POST']) 
@jwt_required()
def create_payment() -> Response:
    """
    Endpoint para crear uno o varios pagos.

    Maneja la creación de un nuevo pago o una lista de pagos masivos a través de una solicitud POST.
    Requiere autenticación JWT y que el rol del usuario sea 'comitiva' y que el pago
    corresponda al servicio asignado al usuario.

    JSON body esperado:
    - Para un pago único: Dict con los datos del pago (incluyendo 'ServiceName').
    - Para pagos masivos: Lista de dicts, donde cada dict es un pago.

    Returns:
        Response: Un objeto de respuesta de Flask con JSON que contiene el
                  estado de la operación (200-205 para éxito, otros para error),
                  un mensaje y, opcionalmente, los datos de la respuesta.

    Raises:
        Exception: Captura cualquier excepción genérica y devuelve una respuesta de error 500.
    """
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_service = claims.get('service', '').strip().lower()

        payment_json = request.json

        if not payment_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        if isinstance(payment_json, list):
            request_service_name = payment_json[0].get('ServiceName', '')
        else:
            request_service_name = payment_json.get('ServiceName', '')
        # print(f"------IMPRIMIENTO INFORMACION DEBUG------")
        # print(f"Rol del usuario: {user_role}")
        # #print(f"Fraccion del usuario: {user_fraction}")
        # print(f"Datos recibidos en la solicitud: {payment_json}")
        # print(f"Servicio solicitado en la petición: {request_service_name}, compara {user_service} con {request_service_name} = {user_service==request_service_name}")
        if user_role != 'comitiva':
            return send_error("No tienes permiso para crear pagos", 403)
        
        if not request_service_name:
                return send_error("Se debe especificar un servicio al crear pago", 400)
            
        if not user_service:
                return send_error("Se debe especificar un servicio", 400)
        
        if request_service_name != user_service: 
            return send_error("No autorizado para crear pagos de este servicio", 403)
    
        estado = 200
        mensaje = ""
        datos = []
        # Se verifica si los datos recibidos son una lista para manejar pagos masivos
        if isinstance(payment_json, list):
            # Se llama a la función de creación de pagos masivos
            print(payment_json)
            estado, mensaje = payment_options.create_check_list_payments(payment_json)
        else:
            # Se llama a la función para crear un solo pago
            estado, mensaje, datos = payment_options.create_payment(payment_json)
                
        # Si el estado está dentro del rango de éxito (200-205), se envía una respuesta exitosa
        if 200 <= estado <= 205:
            return send_success(mensaje, datos, estado)
        else:
            # De lo contrario, se envía una respuesta de error con el estado y mensaje correspondientes
            return send_error(mensaje, estado)
            
    except Exception as e:
        # Se captura cualquier excepción y se devuelve un error 500 con el mensaje de la excepción
        print(f"Error al crear el pago: {e}")
        return send_error(str(e), 500)
    

#Se debe testear esta funcion para ver que ususario podra acceder a cual comitiva
@payment_route.route('read/', methods=['POST'])
@jwt_required()
def read_payment() -> Response:
    """
    Endpoint para la lectura de pagos con filtros.

    Permite obtener un solo pago, todos los pagos o filtrar los pagos por criterios
    específicos. Aplica restricciones de acceso basadas en el rol del usuario:
    - 'delegado': Acceso total, puede ver cualquier servicio (requiere 'serviceName' en el filtro).
    - 'comitiva': Solo puede ver pagos de su servicio asignado.

    JSON body esperado (al menos uno de estos):
    - filters: dict con criterios de filtrado para búsquedas generales.
    - DIM_CustomerId: str para obtener pagos asociados a un cliente específico.
    - serviceName: str (opcional, si no está en 'comitiva', se usa el asignado al user).

    Returns:
        Response: Objeto de respuesta de Flask con JSON que contiene los datos del
                  pago(s) o un mensaje de error.
    """
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_service = claims.get('service', '').strip().lower()

        payment_json = request.json
        #print(f"Rol del usuario: {user_role}, Servicio asignado: {user_service}")

        if not payment_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        request_service_name = payment_json.get('serviceName', '')
        if user_role == 'delegado':
            if not request_service_name:
                return send_error("Se debe especificar un servicio", 400)
            
        elif user_role == 'comitiva':
            if not user_service:
                return send_error("Se debe especificar un servicio", 400)
                # Usuario comitiva: Solo puede ver pagos de su propio servicio.
            #print(f"Comparando servicio del usuario '{user_service}' con el solicitado '{request_service_name}' El resultado es {user_service==request_service_name}")
            if not request_service_name:
                payment_json['serviceName'] = user_service
                request_service_name = user_service
            elif request_service_name != user_service: 
                return send_error("No autorizado para ver pagos de este servicio", 403)
        else:
            return send_error("Rol de usuario no autorizado para crear pagos", 403)
    
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
@role_required('comitiva')
def get_cost() -> Response:
    """
    Endpoint para obtener el costo de un servicio o producto.

    Recibe los parámetros necesarios para que la lógica de negocio calcule el costo
    correspondiente (e.g., el costo actual de un servicio para un cliente).
    Requiere que el usuario tenga el rol 'comitiva'.

    JSON body esperado:
    - serviceName: str, "Nombre del servicio o producto"
    - DIM_CustomerId: str, "ID del cliente"
    (Los campos exactos dependen de la implementación de 'payment_options.get_cost')

    Returns:
        Response: Objeto de respuesta de Flask con JSON que contiene el
                  costo calculado o un mensaje de error.
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
@jwt_required()
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
        claims = get_jwt()
        user_role = claims.get('role')
        if user_role == 'delegado' or user_role == 'comitiva' or user_role == 'subdelegado':
            pass
        else:
            return send_error("No tienes permiso para obtener datos", 403)
        
        # Validar que se recibieron datos JSON en el cuerpo de la solicitud
        data_json = request.json
        if not data_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)

        #print(f"Datos recibidos: {data_json}")

        # Procesar solicitud de costo de servicio por año
        if 'costoservicio' in data_json and data_json['costoservicio']:
            estado, mensaje, datos = payment_options.get_cost_by_payment_year(data_json['costoservicio'])
        
        if 'pagosPendientes' in data_json and data_json['pagosPendientes']:
            print('Se imprimen los la info obtendia')
            for data in data_json['pagosPendientes']:
                
                print(f'El valor es{data}= {data_json['pagosPendientes'][data]}')
            estado, mensaje, datos = payment_options.get_pending_paids_per_customer(data_json['pagosPendientes'])
            print(f"Datos recibidos: {datos}")
            
        if 'servicios_corte_caja' in data_json and data_json['servicios_corte_caja']:
            estado, datos = hanlder_cash_cut.get_service_chosen(data_json['servicios_corte_caja'])
            mensaje = "Datos obtenidos correctamente"
            print(f"Datos recibidos: {datos}")
            
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
    


@payment_route.route('cash_cut/', methods=['POST'])
@role_required('comitiva')
def cash_cut_route() -> Response:
    """
    Ruta para realizar un corte de caja.

    Esta ruta acepta una solicitud POST con un cuerpo JSON que contiene los datos
    necesarios para realizar un corte de caja de un servicio específico.
    Delega la lógica principal a la clase `cashCutCrud`.

    Args:
        None (los datos se reciben del cuerpo de la solicitud HTTP).

    Returns:
        Response: Un objeto de respuesta HTTP.
                  - Si el corte de caja es exitoso, devuelve un mensaje de éxito con estado 201.
                  - Si hay un error de validación de datos o de lógica de negocio,
                    devuelve un mensaje de error con el estado correspondiente (e.g., 400).
                  - Si ocurre una excepción inesperada, devuelve un mensaje de error con estado 500.

    Recibe los siguientes campos en el cuerpo JSON:
        - DIM_ServiceDetailesType (str): El tipo de servicio (e.g., "energia", "telecomunicaciones").
        - DIM_ServiceOwnersId (str): El ID del propietario del servicio.
        - DIM_service (str): El nombre del servicio (e.g., "luz", "internet").
    """
    try:
        data_json = request.json
        if not data_json:
            return send_error("No se recibieron datos en el cuerpo de la solicitud", 400)
        
        estado, mensaje = hanlder_cash_cut.CashCut(data_json)
        print(f"Estado: {estado}, Mensaje: {mensaje}")
        if estado == 201:
            return send_success(mensaje, None, estado)
        else:
            return send_error(mensaje, estado)
    except Exception as e:
        print(f"Error al obtener el costo: {e}")
        return send_error(str(e), 500)


@payment_route.route('generar_servicio/', methods=['POST'])
@role_required('comitiva')
def insert_new_service() -> Response:
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
        
        estado, mensaje = service_details_options.insert_service_details(cost_json)

        if 200 <= estado <= 205:
            return send_success(mensaje, None, estado)
        else:
            return send_error(mensaje, estado)
            
    except Exception as e:
        print(f"Error al obtener el costo: {e}")
        return send_error(str(e), 500)
    


