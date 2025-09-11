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
        necesarios e inserta el registro de pago en la base de datos.

        Args:
            data_json (dict): Un diccionario con los datos del pago. Debe contener los
                              campos requeridos.

        Returns:
            tuple[int, Any]: Una tupla con el código de estado HTTP y un mensaje.
                             - (400, "message"): Datos faltantes o inválidos.
                             - (500, "message"): Error interno del servidor.
                             - (201, "message"): Pago creado exitosamente.
        """
        # print('Mostrando desde create payments')
        # for dato in data_json:
        #     print(f'El dato es: {dato} con el valor de: {type(dato)}')

        #Hacer validaciones para que no pasen cuentas de tipo estudiante o inactivas
        #pasar amount a float
        #SE DEBEN AGREGAR MULTIPLES VALIDACIONES se agregan en la funcionb para crear EL FACT REVENUE PARA QUE NO SE CREEN PAGOS PARA ETX ETX
        data_json['amount'] = float(data_json['amount'])
        data_json['FactAmount'] = float(data_json['FactAmount'])
        data_json['AnioPago'] = str(data_json['AnioPago'])
        fields_required = ['DIM_OnwerCustomerId', 'DIM_AccountId', 'DIM_CustomerId', 'ServiceName', 'serviceDetailsType', 'AnioPago','movementName', 'entrada', 'FactAmount', 'amount']
        for dato in data_json:
            print(f"El dato es: {dato} con el valor de: {type(dato)}")
        type_fields = [str, str, str, str, str,  str, str, str, float, float]

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


            return 201, "Pago creado satisfactoriamente", []
        
        except Exception as e:
            # Capturar cualquier excepción inesperada y devolver un error del servidor
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
                print(f"Se aplicaran filtros a la consulta {filters['filters']}    {filters['serviceName']} ")
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
        """Obtiene el costo de un servicio o producto basado en los datos proporcionados.

        Esta función valida los datos de entrada, Ademas debera buscar cuales son los pagos que ese cliente en especifico puede pagar, 
        para lograr eso se deben hacer peticiones, de que cuentas ya pagaron, ya que recordemos que cada cliente puede tener ciertas cuentas
        ademas se debe ir haciendo esto verificando por anio,  una vez hecho esto, se deberan devolver las cuentas que el 
        cliente aun no ha pagado para poder realizar el pago,

        Args:
            data_json (dict): Un diccionario con los datos necesarios para calcular el costo.

        Returns:
            tuple[int, str, list]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                             - (400, "message"): Datos faltantes o inválidos.
                             - (500, "message"): Error interno del servidor.
                             - (200, data): Costo calculado.
                             - list: Una lista de dict los cuales contienen la ifnormacin
                             de pagos que el cliente puede realizar.
        """
        account_handler = AccountCrud()
        service_handler = DIM_Service()

        fields_required = ['ServiceName', 'DIM_CustomerId']
        type_fields = [str, str]

        is_valid, message = validate_data(data_json, fields_required, type_fields, "payment")

        if not is_valid:
            return 400, message, []
        
        data_format = {
            "id_user": data_json['DIM_CustomerId'],
        }
        #oBTENER PRIMERO TODAS LA CUENTAS ASOCIADAS AL CLIENTE
        codigo_esta, mensaje, cuentas = account_handler.read_account(data_format)
        print("pasamo obquiero cuentas")
        if codigo_esta != 200:
            return codigo_esta, mensaje, []
        
        
        id_accounts = [cuenta['DIM_AccountId'] for cuenta in cuentas]  # Obtener los IDs de las cuentas


        print("pasamo cuenta")
        #Se generaran los anios desde los que se va a buscar \
        anios_filtro = [anio for anio in range(2020, datetime.now().year + 1)]

        service_id = service_handler.get_service_id(data_json['ServiceName'])
        service_details_ids = get_service_detailsId_by_ServiceId(service_id)

        print(id_accounts)
        print(anios_filtro)
        print(service_details_ids)


        #data = get_pending_pays(anios_filtro, id_accounts, data_json['ServiceName'])
        # code, data = dim_service_details_handler.get_service_by_date_servicetype(data_json)
        # if code != 200:
        #     print(f"Error al obtener el costo: {data}")
        #     return code, "No se pudo obtener el costo", []
        
        # return code, "Costo obtenido satisfactoriamente", data
        return 200, "nla bla bkla", []
    

    def read_payments_customer_id(self, filters: dict) -> tuple[int, Any, list]:
        """Lee los registros de pagos basados en los filtros proporcionados.

        Esta función valida los filtros, obtiene los registros de pagos
        correspondientes y devuelve el resultado.

        Args:
            filters (dict): Un diccionario con los filtros para la búsqueda de pagos.

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
        """Obtiene el costo de un servicio o producto basado en los datos proporcionados.

        Esta función valida los datos de entrada, Ademas debera buscar cuales son los pagos que ese cliente en especifico puede pagar, 
        para lograr eso se deben hacer peticiones, de que cuentas ya pagaron, ya que recordemos que cada cliente puede tener ciertas cuentas
        ademas se debe ir haciendo esto verificando por anio,  una vez hecho esto, se deberan devolver las cuentas que el 
        cliente aun no ha pagado para poder realizar el pago,

        Args:
            data_json (dict): Un diccionario con los datos necesarios para calcular el costo.

        Returns:
            tuple[int, str, list]: Una tupla con el código de estado HTTP y los datos o un mensaje.
                             - (400, "message"): Datos faltantes o inválidos.
                             - (500, "message"): Error interno del servidor.
                             - (200, data): Costo calculado.
                             - list: Una lista de dict los cuales contienen la ifnormacin
                             de pagos que el cliente puede realizar.
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
            if  not amount:
                print(f"Error al leer la cantidad: {amount}")
                return 400, f"No se encontraron costos de Servicos registrados en {data_json['Year']}", []
            
            return 200, "Datos obtenidos satisfactoriamente", amount
        except Exception as e:
            print(e)
            # Capturar cualquier excepción inesperada y devolver un error del servidor
            return 500, f"Error leyendo los pagos: {str(e)}", []
        
    def update_payment_view(self, data_json: dict) -> tuple[int, Any, list]:
        """
        documentar correctamnete
        """
        try:
            status, datos = payments_handler.update_payment_view(data_json['ServiceName'], data_json['DIM_CustomerId'], data_json['AnioPago'])
            if status != 200:
                print(f"Error al leer los pagos: {status}")
                return []
            return datos
        except Exception as e:
            print(e)
            return []