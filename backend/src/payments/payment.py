from typing import Any, Literal
from src.utils.validate_data import validate_data
from src.fact_revenues.Fact_revenue import factRevenueCrud 
from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud
from src.dim_serviceonwers.dim_serviceOnwers import DIM_ServiceOnwersCrud

# Se importa la funcion para obtener el id de detalles del servicio
from src.dim_servicedetails.repository.show import get_service_detailsID

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
                
                return 201, "Pago creado satisfactoriamente", data
        except Exception as e:
            print(e)
            return 500, f"Error creando el pago: {str(e)}", []


    def read_payments(self, filters: dict) -> tuple[int, Any, list]:
        """Lee los registros de pagos basados en los filtros proporcionados.

        Esta función valida los filtros, obtiene los registros de pagos
        correspondientes y devuelve el resultado.

        Args:
            filters (dict): Un diccionario con los filtros para la búsqueda de pagos.
            {
            manzana: list[str],
            dim_date: str,
            dim_status: str
            }

        Returns:
            tuple[int, Any]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                             - (400, "message"): Filtros inválidos.
                             - (500, "message"): Error interno del servidor.
                             - (200, data): Datos de pagos encontrados.
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
                print(f"Se aplicaran filtros a la consulta {filters['filters']}     {filters['serviceName']} ")
                #Cuando se proporcionan filtros se deben aplicar los filtros a la consulta
                code, data = payments_handler.get_payments_with_filters(filters['serviceName'], filters['filters'])

                if code != 200:
                    print(f"Error al leer los pagos: {data}")
                    return code, "Error a la hora de aplicar filtros", []
                
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
        print(filters)
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
        for dato in data_json:
            print(f"El dato es: {dato} con el valor de: {type(dato)}")
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
        """Actualiza la vista de pagos pendientes.

        Esta función se utiliza para actualizar la vista de pagos pendientes de un cliente
        para un servicio y año específicos después de que se ha realizado un pago.
        
        Args:
            data_json (dict): Un diccionario con los datos necesarios para la actualización,
                              incluyendo 'ServiceName', 'DIM_CustomerId', 'AnioPago'.
        
        Returns:
            Any: Los datos actualizados si la operación fue exitosa, de lo contrario una lista vacía.
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