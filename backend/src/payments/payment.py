from typing import Any, Literal
from src.utils.validate_data import validate_data
from src.fact_revenues.Fact_revenue import factRevenueCrud 
from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud
from src.dim_serviceonwers.dim_serviceOnwers import DIM_ServiceOnwersCrud

# Se importa la funcion para obtener el id de detalles del servicio
from src.dim_servicedetails.repository.show import get_service_detailsID, get_amount_by_id  

fact_revenue_handler = factRevenueCrud()
dim_service_details_handler = ServiceDetailsCrud()
handler_dim_service_owner = DIM_ServiceOnwersCrud()

#importaciones para Buscar un pago pendiente
from src.accounts.account import AccountCrud
from src.payments.repository.get_pending_pays import get_pending_pays
from datetime import datetime
from src.dim_service.DIM_Service import DIM_Service
from src.dim_servicedetails.repository.show import get_service_detailsId_by_ServiceId

#importaciones de mostrar pagos
from src.payments.repository.read_payments import ReadPayment

#Aqui
from src.payments.repository.get_fact_revenues_customer import get_fact_revenues_by_customer_id
payments_handler = ReadPayment()

#Importaciones de validaciones de pagos Pendiente
from src.payments.services.validate_payment import ValidatePayment

validate_payment = ValidatePayment()

#Importacion para saber le costo de un servicio en especidico en un anio especifico
from src.dim_servicedetails.repository.show import get_amount_by_service_and_date

#Importaciones del check list
from src.payments.repository.get_check_list import get_check_list
from src.payments.services.check_list_services import is_service_valid, get_check_list_valids
class PaymentCrud:
    """Clase para manejar las operaciones CRUD de pagos."""

    def create_payment(self, data_json: dict) -> tuple[int, Any]:
        """Crea un nuevo registro de pago en la tabla FACT_Revenue.

        Esta función valida los datos de entrada, obtiene los IDs de servicios
        necesarios e inserta el registro de pago en la base de datos. También
        actualiza la vista de pagos pendientes si la entrada es un pago.

        Args:
            data_json (dict): Un diccionario con los datos del pago. Debe contener:
                - DIM_OnwerCustomerId (str): ID del propietario del cliente
                - DIM_AccountId (str): ID de la cuenta
                - DIM_CustomerId (str): ID del cliente
                - ServiceName (str): Nombre del servicio (ej: 'agua', 'feria')
                - serviceDetailsType (str): Tipo de detalle del servicio
                - AnioPago (str): Año del pago
                - movementName (str): Nombre del movimiento
                - entrada (str): Tipo de entrada
                - FactAmount (float): Monto facturado
                - amount (float): Monto del pago

        Returns:
            tuple[int, Any]: Una tupla con:
                - Código de estado HTTP
                - Mensaje descriptivo
                - Lista de datos adicionales (vacía en caso de error)
            
            Códigos de retorno:
                - 400: Datos faltantes, inválidos o validaciones fallidas
                - 500: Error interno del servidor
                - 201: Pago creado exitosamente

        Raises:
            No levanta excepciones directamente, pero retorna códigos de error.

        Examples:
            >>> payment_data = {
            ...     'DIM_OnwerCustomerId': '123',
            ...     'DIM_AccountId': '456',
            ...     'ServiceName': 'agua',
            ...     'serviceDetailsType': 'consumo',
            ...     'AnioPago': '2024',
            ...     'amount': 150.50
            ... }
            >>> PaymentCrud().create_payment(payment_data)
            (201, 'Pago creado satisfactoriamente', [])
        
        Notes:
            - Convierte automáticamente amount y FactAmount a float
            - Valida que la cuenta no sea de estudiante o inactiva
            - Verifica que no existan pagos pendientes duplicados
            - Aplica reglas de negocio específicas para diferentes servicios
        """
        data_json['amount'] = float(data_json['amount'])
        data_json['FactAmount'] = float(data_json['FactAmount'])
        data_json['AnioPago'] = str(data_json['AnioPago'])
        fields_required = ['DIM_OnwerCustomerId', 'DIM_AccountId', 'DIM_CustomerId', 'ServiceName', 'serviceDetailsType', 'AnioPago','movementName', 'entrada', 'FactAmount', 'amount']

        type_fields = [str, str, str, str, str, str, str, str, float, float]

        is_valid, message = validate_data(data_json, fields_required, type_fields, "payment")

        if not is_valid:
            return 400, message, []
        
        #Validar si no existe otro pago pendiente 
        is_valid, message = validate_payment.is_payment_active(data_json['DIM_CustomerId'], data_json['AnioPago'], data_json['ServiceName'], data_json['entrada'], data_json['serviceDetailsType'])
        if not is_valid:
            return 400, message, []
        
        #Validar que Amount sea una cantidad positiva
        is_valid = data_json['amount'] >= 0
        if not is_valid:
            return 400, "La cantidad ingeresada debe ser mayor a 0 Pesos", []
        
        is_valid = validate_payment.is_account_active(data_json['DIM_AccountId'])
        if not is_valid:
            return 400, "Las personas registradas como inactivas o estudiantes no puede realizar pagos", []
        try:
            # Obtener el ID del detalle del servicio
            dim_service_detail_id = get_service_detailsID(data_json['serviceDetailsType'], data_json["AnioPago"], data_json['ServiceName'])
            
            # Si el ID no existe, devolver un error
            if not dim_service_detail_id:
                return 400, f"serviceDetailsType '{data_json['serviceDetailsType']}' no se encontró.", []

            data_json['DIM_ServiceDetailsId'] = dim_service_detail_id

            # Crear el registro de ingresos en la tabla de facturación
            code, message = fact_revenue_handler.create_fact_revenue(data_json)
            
            if code != 201:
                return code, message, []
            
            # AQUI SE APLICA LA LOGICA DE ACTUALIZACION DEL PAGO PENDIENTE 
            if data_json['entrada'] == "":
                data = self.update_payment_view(data_json)
                if not data:
                    return 400, "No se pudo actualizar el pago pendiente", []
                else:
                    return 201, "Pago creado satisfactoriamente", data
            
            else:
                return 201, "Pago creado satisfactoriamente", []
        except Exception as e:
            print(e)
            return 500, f"Error creando el pago: {str(e)}", []

    def read_payments(self, filters: dict) -> tuple[int, Any, list]:
        """
        Lee y filtra registros de pagos según los criterios especificados.
        
        Esta función procesa solicitudes de consulta de pagos, aplicando validaciones
        básicas y delegando la obtención de datos al módulo de manejo de pagos.
        Soporta dos modos de operación: sin filtros (obtiene todos los registros del servicio)
        y con filtros aplicados (consulta específica con criterios definidos).

        Args:
            filters (dict): Diccionario que contiene los parámetros de filtrado con la estructura:
                {
                    'serviceName': str,       # Nombre del servicio a consultar
                    'filters': dict           # Diccionario con criterios de filtrado específicos
                    # Los filtros pueden incluir:
                    #   - manzana: list[str]   # Lista de manzanas/áreas
                    #   - dim_date: str        # Fecha de referencia
                    #   - dim_status: str      # Estado de los pagos
                }

        Returns:
            tuple[int, Any, list]: Tupla con tres elementos:
                - int: Código de estado HTTP:
                    * 400: Filtros inválidos o errores de validación
                    * 500: Error interno del servidor
                    * 200: Consulta exitosa
                - Any: Mensaje descriptivo del resultado o datos de error
                - list: Lista con los datos de pagos encontrados. En caso de aplicar filtros,
                        incluye adicionalmente un diccionario con datos de checklist en el último
                        elemento con formato: {tuple(servicios_validos): check_lista_data}

        Flujo de ejecución:
        1. Valida la estructura básica de los filtros recibidos
        2. Si no hay filtros específicos ('filters' vacío):
           - Obtiene todos los registros del servicio especificado
        3. Si hay filtros específicos ('filters' no vacío):
           - Aplica los filtros a la consulta
           - Genera información adicional de checklist si hay servicios válidos
        4. Maneja excepciones y errores durante el proceso

        Raises:
            Exception: Captura cualquier error inesperado y lo devuelve como error 500
        """
        
        fields_required = ['serviceName', 'filters']
        type_fields = [str, dict]
        is_valid, message = validate_data(filters, fields_required, type_fields, "payment")

        if not is_valid:
            return 400, message, []
        
        try:
            if filters['filters'] == {}:
                #Cuando no se proporcionan filtros solo se devuelven todos los registros del servicio
                code, data = payments_handler.get_payments_by_service(filters['serviceName'], {})

                if code != 200:
                    print(f"Error al leer los pagos: {data}")
                    return code, "No se encontraron pagos", []
                
                #print(f"Code: {code}, Data: Datos creados satisfactoriamente, /n {data[0]}")
                
                return code, "Datos obtenidos satisfactoriamente", data
            #CASO 2
            elif filters['filters'] != {}:
                #print(f"Se aplicaran filtros a la consulta {filters['filters']}     {filters['serviceName']} ")
                #Cuando se proporcionan filtros se deben aplicar los filtros a la consulta
                code, data = payments_handler.get_payments_with_filters(filters['serviceName'], filters['filters'])

                if code != 200:
                    print(f"Error al leer los pagos: {data}")
                    return code, "Error a la hora de aplicar filtros", []
                
                print(f"tamaanio de data: {len(data)}")
                #Codigo para obtener el check list
                servicios_validos = get_check_list_valids(filters['filters']['DIM_Date'], filters['serviceName'])
                
                print(f"Servicios validos: {servicios_validos}") 
                if servicios_validos: 
                    status, mensaje_query, check_lista_data = self.get_check_list_table() 
                    
                    data_tuple = (servicios_validos,check_lista_data)
                    # Crear el diccionario con la tupla como clave 
                    data_format = {'servicios_validos': data_tuple} 
                    # Agregar el diccionario a data 
                    data.append(data_format)
                
                #print(f"Code: {code}, Data: Datos creados satisfactoriamente, /n {data[0]}")
                return code, "Datos obtenidos satisfactoriamente", data
            else:
                return 400, "Filtros inválidos", []
                
        except Exception as e:
            print(e)
            # Capturar cualquier excepción inesperada y devolver un error del servidor
            return 500, f"Error leyendo los pagos: {str(e)}", []
        
    def get_cost(self, data_json: dict) -> tuple[int, Any, list]:
        """Obtiene una lista de pagos pendientes para un cliente y servicio específicos.

            Esta función valida los datos de entrada y busca los pagos pendientes
            asociados a las cuentas del cliente para un servicio y años específicos.

            Args:
                data_json (dict): Un diccionario con los datos necesarios para la búsqueda.
                                Debe contener 'ServiceName' y 'DIM_CustomerId'.

            Returns:
                tuple[int, str, list]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                                        - (400, "message"): Datos faltantes o inválidos.
                                        - (500, "message"): Error interno del servidor.
                                        - (200, "message", data): Lista de pagos pendientes.
            """
        # Define los campos requeridos y sus tipos para la validación de los datos de entrada.
        fields_required = ['ServiceName', 'DIM_CustomerId']
        type_fields = [str, str]

        # Llama a una función de utilidad para validar si los datos de entrada son correctos.
        # 'is_valid' será un booleano y 'message' contendrá el error si los datos no son válidos.
        is_valid, message = validate_data(data_json, fields_required, type_fields, "payment")

        # Si los datos no son válidos, retorna un código de error 400.
        if not is_valid:
            return 400, message, []
        
        try:
            # Intenta obtener los pagos pendientes usando los datos del JSON.
            data = get_pending_pays(data_json['DIM_CustomerId'], data_json['ServiceName'])
            
            # Si la función get_pending_pays retorna None, significa que no se encontraron
            # pagos pendientes. Se imprime un mensaje y se retorna un código 400.
            if data is None:
                print(f"Error al obtener los pagos pendientes: {data}")
                return 400, "No se encontraron pagos pendientes", []
            
            # Si todo es correcto, retorna un código 200 con la lista de pagos.
            return 200, "Datos obtenidos satisfactoriamente", data
        
        except Exception as e:
            # Captura cualquier excepción que ocurra durante el proceso, imprime el error
            # en la consola y retorna un código de error 500 para indicar un fallo interno.
            print(e)
            return 500, f"Error leyendo los pagos: {str(e)}", []
        

    def read_payments_customer_id(self, filters: dict) -> tuple[int, Any, list]:
        """Lee los registros de pagos de un cliente basados en los filtros proporcionados.

        Esta función valida los filtros, obtiene los registros de pagos
        correspondientes a un cliente y devuelve el resultado.

        Args:
            filters (dict): Un diccionario con los filtros para la búsqueda de pagos.
                            Debe contener 'DIM_CustomerId', 'serviceName', 'service_type', 'Year'.

        Returns:
            tuple[int, Any]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                             - (400, "message"): Filtros inválidos.
                             - (500, "message"): Error interno del servidor.
                             - (200, data): Datos de pagos encontrados.
        """
        #print(filters)
        fields_required = ['DIM_CustomerId', 'serviceName', 'service_type', 'Year']
        type_fields = [str, str, str, str]
        is_valid, message = validate_data(filters, fields_required, type_fields, "payment")

        if not is_valid:
            return 400, message, []
        
        try:
            
            #Cuando no se proporcionan filtros solo se devuelven todos los registros del servicio
            code, data = get_fact_revenues_by_customer_id(**filters)

            if code != 200:
                print(f"Error al leer los pagos: {data}")
                return code, "No se encontraron pagos", []
            
            return code, "Datos obtenidos satisfactoriamente", data
        except Exception as e:
            print(e)
            # Capturar cualquier excepción inesperada y devolver un error del servidor
            return 500, f"Error leyendo los pagos: {str(e)}", []
        

    def get_cost_by_payment_year(self, data_json: dict) -> tuple[int, Any, list]:
        """Obtiene el costo de un servicio en un año específico.

        Esta función valida los datos de entrada y busca el costo del servicio
        basándose en el tipo de servicio, año y nombre del servicio.

        Args:
            data_json (dict): Un diccionario con los datos necesarios para calcular el costo.
                              Debe contener 'service_type', 'Year', 'ServiceName'.

        Returns:
            tuple[int, str, list]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                                   - (400, "message"): Datos faltantes o inválidos.
                                   - (500, "message"): Error interno del servidor.
                                   - (200, data): Costo del servicio.
        """
        handler_service = DIM_Service()
        # for dato in data_json:
        #     print(f"El dato es: {dato} con el valor de: {type(dato)}")
        fields_required = ['service_type', 'Year', 'ServiceName']
        type_fields = [ str, str, str]
        is_valid, message = validate_data(data_json, fields_required, type_fields, "payment")

        if not is_valid:
            return 400, message, []
        
        try:
            last_two_digits = data_json['Year'][-2:]

            serviceId = handler_service.get_service_id(data_json['ServiceName'])

            #Cuando no se proporcionan filtros solo se devuelven todos los registros del servicio
            amount = get_amount_by_service_and_date(data_json['service_type'], f"Y{last_two_digits}", serviceId)

            #print(f"Se imprimieran todos los datsos obtenidos emepzando desde los datos de json \n {data_json['service_type']} \n {data_json['Year']} \n {amount} \n {year} \n Y{last_two_digits}")
            if not amount:
                print(f"Error al leer la cantidad: {amount}")
                return 400, f"No se encontraron costos de Servicos registrados en {data_json['Year']}", []
            
            return 200, "Datos obtenidos satisfactoriamente", amount
        except Exception as e:
            print(e)
            # Capturar cualquier excepción inesperada y devolver un error del servidor
            return 500, f"Error leyendo los pagos: {str(e)}", []
        
        
    def update_payment_view(self, data_json: dict) -> Any:
        """
        Actualiza la vista de pagos pendientes después de realizar un pago.
        
        Esta función se ejecuta después de un proceso de pexitoso para refrescar la información
        visualizada al usuario, mostrando el nuevo estado de los pagos del cliente para el servicio
        y año específicos.

        Args:
            data_json (dict): Diccionario con los parámetros necesarios para la actualización:
                {
                    'ServiceName': str,           # Nombre del servicio afectado
                    'DIM_CustomerId': str,        # Identificador único del cliente
                    'AnioPago': str,              # Año del pago realizado
                    'serviceDetailsType': str     # Tipo de detalle del servicio
                }

        Returns:
            Any: Retorna una de las siguientes opciones:
                - list: Lista con los datos actualizados de la vista de pagos
                - []: Lista vacía en caso de error durante el proceso

        Note:
            La función maneja errores internamente y devuelve lista vacía en caso de excepción
            para evitar interrumpir el flujo de la aplicación.
        """
        try:
            status, datos = payments_handler.update_payment_view(data_json['ServiceName'], data_json['DIM_CustomerId'], data_json['AnioPago'], data_json['serviceDetailsType'])
            if status != 200:
                print(f"Error al leer los pagos: {status}")
                return []
            return datos
        except Exception as e:
            print(e)
            return []
        

    def get_check_list_table(self):
        """
        Obtiene la lista de checklist para el módulo de pagos.
        
        Esta función proporciona los datos necesarios para construir la interfaz de checklist
        que acompaña a la vista principal de pagos. Incluye validaciones para evitar duplicados
        y asegurar la integridad de la información.

        Returns:
            tuple[int, str, list]: Tupla con tres elementos:
                - int: Código de estado HTTP (200 exitoso, 500 error)
                - str: Mensaje descriptivo del resultado de la operación
                - list: Lista con los datos del checklist o lista vacía en caso de error

        Note:
            La función está diseñada para ser llamada durante la carga inicial de la vista de pagos
            o como parte de una actualización asíncrona de la interfaz.
        """
        try:
            return 200, "Datos obtenidos satisfactoriamente", get_check_list()
        except Exception as e:
            print(e)
            return 500, "Error leyendo el check list", []
    

    def create_check_list_payments(self, payment_json: list):
        """
        Procesa y almacena un nuevo registro de checklist en la base de datos.
        
        Esta función aplica la lógica de negocio completa para la creación de checklist,
        incluyendo validaciones, transformación de datos y persistencia en la base de datos.

        Args:
            data_json (dict): Diccionario con los datos del checklist a crear. La estructura
                             específica depende de los requisitos del formulario de entrada.

        Returns:
            Nota: La función actualmente no tiene implementado el valor de retorno. Se recomienda
            completar con la lógica de retorno apropiada (tuple[int, str, Any] o similar).

        Todo:
            - Implementar la lógica completa de validación y inserción
            - Definir el formato de retorno consistente con otras funciones
            - Agregar manejo de excepciones y logging de errores
        """
        for data_json in payment_json:
            data_json['amount'] = float(data_json['amount'])
            data_json['FactAmount'] = float(data_json['FactAmount'])
            data_json['AnioPago'] = str(data_json['AnioPago'])
            fields_required = ['DIM_OnwerCustomerId', 'DIM_AccountId', 'DIM_CustomerId', 'ServiceName', 'serviceDetailsType', 'AnioPago','movementName', 'entrada', 'FactAmount', 'amount']
            
            type_fields = [str, str, str, str, str, str, str, str, float, float]
            is_valid, message = validate_data(data_json, fields_required, type_fields, "payment")
            
            if not is_valid:
                return 400, message
            
            #Validar si no existe otro pago pendiente 
            is_valid, message = validate_payment.is_payment_active(data_json['DIM_CustomerId'], data_json['AnioPago'], data_json['ServiceName'], data_json['entrada'], data_json['serviceDetailsType'])
            if not is_valid:
                return 400, message
            
        try:
            # Crear el registro de ingresos en la tabla de facturación
            code, message = fact_revenue_handler.insert_many_register(payment_json)
            
            if code != 201:
                return code, message
            
            return 201, "Pagos creados exitosamente"
        except Exception as e:
            print(e)
            return 500, f"Error leyendo el check list: {str(e)}"