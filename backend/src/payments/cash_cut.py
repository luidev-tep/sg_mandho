from src.payments.repository.cash_cut_querys import create_cash_cut_register, found_pending, search_service_Valid, is_service_exist
from src.payments.model.pending_paid import CashCutModel
from src.utils.id_generator import create_id
from src.utils.validate_data import validate_data
from typing import Any
from src.fact_revenues.models.fact_revenue import FACT_Revenue
from src.dim_dates.dim_date import DIM_DATE

# importacion para obtener el estado del pago
from src.dim_status.status import DIM_status

from src.fact_revenues.repository.insert import insert_many_fact_revenues
# Importacion del handler de movimiento
from src.dim_movement.DIM_movent import DIM_Movement

from src.dim_servicedetails.repository.show import get_service_detailsID

from src.fact_revenues.services.service import get_status_payment

from src.dim_service.DIM_Service import DIM_Service
handler_services = DIM_Service()

from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud
hanlder_service_details = ServiceDetailsCrud()
handler_movement = DIM_Movement()
handler_status = DIM_status()

from src.payments.payment import PaymentCrud

class cashCutCrud(PaymentCrud):
    """
    Clase para la gestión de los cortes de caja (cash cut).
    Hereda de PaymentCrud para reutilizar la lógica de pagos.
    Esta clase contiene las funciones necesarias para procesar los servicios,
    encontrar cuentas pendientes, generar registros de ingresos y finalmente
    crear el registro del corte de caja.
    """
    def CashCut(self, data_json: dict) -> tuple[int, Any]:
        """
        Función principal para crear un corte de caja.
        
        Realiza las siguientes acciones:
        1. Valida los datos de entrada.
        2. Verifica que el servicio no sea "agua", ya que no se pueden realizar cortes de caja para este.
        3. Busca el ID del detalle del servicio.
        4. Valida si el servicio es elegible para un corte de caja.
        5. Encuentra todas las cuentas con pagos pendientes para el servicio especificado.
        6. Genera registros de ingresos (FACT_Revenue) para cada cuenta pendiente, 
           marcando el monto como 0.
        7. Inserta los registros de ingresos en la base de datos.
        8. Crea el registro final del corte de caja con la cantidad de registros generados.

        Args:
            data_json (dict): Un diccionario con los datos del servicio a cortar,
                              incluyendo 'DIM_ServiceDetailesType', 'DIM_ServiceOwnersId' y 'DIM_service'.

        Returns:
            tuple[int, Any]: Una tupla que contiene el código de estado HTTP y un mensaje o datos.
                             - 201 y un mensaje de éxito si el corte de caja se realizó correctamente.
                             - 400 y un mensaje de error si los datos son inválidos o el servicio no es elegible.
                             - 500 y un mensaje de error si ocurre un problema durante la inserción en la base de datos.
        """
        field_required = ['DIM_ServiceDetailesType','DIM_ServiceOwnersId', 'DIM_service']
        type_filed = [str, str, str]
        is_valid, message = validate_data(data_json, field_required, type_filed, "cash_cut")
        
        if not is_valid:
            return 400, message
        
        if data_json['DIM_service'] == "agua":
            return 400, "No se puede hacer un corte de caja para agua"
        
        handler_date = DIM_DATE()
        date = handler_date.full_date
        
        #Se inicializa antes ya que sera insertado en fact Revenues
        DIM_serviceDatilsId = get_service_detailsID(data_json['DIM_ServiceDetailesType'], date[0], data_json['DIM_service']) #Para simbolizxar que se envia el anio
        data_json['DIM_ServiceDetailsId'] = DIM_serviceDatilsId
        
        pending_accounts = found_pending(data_json['DIM_ServiceDetailesType'], data_json['DIM_service'])
        data_format = []
        
        #Validacion final del servicio
        if not search_service_Valid(date[0], DIM_serviceDatilsId):
            return 400, f"No se puede hacer un corte de caja para el servicio {data_json['DIM_ServiceDetailesType']}"
        
        
        # Crear registros de fact_revenue para las cuentas pendientes
        if pending_accounts:
            data_format = self.__Fact_revenues_registers(pending_accounts, data_json)
        
        if not data_format:
            return 500, "Error al crear los registros de fact_revenue pendientes"
        
        # for data in data_format:
        #   print(data)
        response = insert_many_fact_revenues(data_format)
        
        if not response:
            return 500, "Error al insertar los registros de fact_revenue"
        
        data_cash_cut = {
            "DIM_CountRegisters": len(data_format),
            "DIM_ServiceDetailsId": DIM_serviceDatilsId,
            "DIM_DateId": handler_date.dateId,
            "DIM_ServiceOwnersId": data_json['DIM_ServiceOwnersId']
            }
        # print(data_cash_cut['DIM_CountRegisters'])
        # print(data_cash_cut['DIM_ServiceDetailsId'])
        # print(data_cash_cut['DIM_DateId'])
        # print(data_cash_cut['DIM_ServiceOwnersId'])
        status, message = self._create_cash_cut(data_cash_cut)
        
        if status != 201:
            return status, message
        mensaje = f"Se hizo el corte de caja exitosamente, Se crearon {data_cash_cut['DIM_CountRegisters']} registros"
        return status, mensaje
        
    def __Fact_revenues_registers(self, pending_accounts: list, data_json: dict) -> list[FACT_Revenue] | bool:
        """
        Crea múltiples registros de FACT_Revenue para cuentas pendientes.

        Itera sobre una lista de cuentas pendientes y genera un registro de FACT_Revenue
        para cada una, marcando el monto pagado como 0 y asignando un estado de pago "incompleto".
        
        Args:
            pending_accounts (list): Una lista de tuplas con los datos de las cuentas pendientes.
            data_json (dict): Diccionario con los datos del corte de caja, incluyendo 
                              el ID del detalle del servicio y el tipo de servicio.

        Returns:
            list[FACT_Revenue] | bool: Una lista de objetos FACT_Revenue si la generación de registros fue exitosa,
                                       de lo contrario, False.
        """
        data_format = []
        dim_date_data = DIM_DATE()
        year = str(dim_date_data.dateId)
        
        # Obtener el movementId para el cash cut (usamos un movimiento específico para pendientes)
        movement_id = handler_movement.get_movement_id("ingreso")
        
        for account in pending_accounts:
            
            # Generar hash único para la cuenta primero
            account_hash = create_id([account[0]])
            
            
            # Crear FACT_RevenueId usando el hash de la cuenta en lugar del amount
            id = create_id([account_hash, data_json['DIM_ServiceDetailesType'], year[4:]])
            
            fact_revenueId = create_id([id, data_json['DIM_ServiceDetailsId'], account[0]])
            
            # Obtener el estado para montos pendientes (0 amount)
            # En la función get_status_payment, un monto_pagado de 0 debería mapearse a un estado específico.
            status = get_status_payment(1000.0, 0.0)
            estatus_id = handler_status.get_status_id(status, "fact_revenue")
            
            if not estatus_id:
                # Usar estado por defecto si no se encuentra
                return False
            
            data_item = {
                'FACT_RevenueId': fact_revenueId,
                'DIM_DateId': dim_date_data.dateId,
                'DIM_AccountId': account[0],
                'DIM_ServiceDetailsId': data_json['DIM_ServiceDetailsId'],
                'DIM_MovementId': movement_id,
                'DIM_StatusId': estatus_id,
                'amount': 0,  # Monto pagado se marca como 0
            }
            data_format.append(FACT_Revenue(**data_item))
        
        return data_format
    
    def _create_cash_cut(self, data_json: dict) -> tuple[int, Any]:
        """
        Función privada para insertar un nuevo registro en la tabla DIM_CashCut.

        Esta es la función final que se ejecuta después de toda la lógica de negocio
        para registrar el corte de caja en la base de datos.
        
        Args:
            data_json (dict): Un diccionario con los datos del corte de caja,
                              incluyendo la cantidad de registros, IDs de servicio, fecha y dueño.

        Returns:
            tuple[int, Any]: Una tupla con el código de estado HTTP y un mensaje.
                             - 201 y un mensaje de éxito si el registro se creó correctamente.
                             - 500 y un mensaje de error si ocurre un problema.
        """
        try:
            #Insertar el nuevo registro a la base de datos
            data_json['DIM_CashCutId'] = create_id([data_json['DIM_ServiceDetailsId'], data_json['DIM_ServiceOwnersId'], data_json['DIM_CountRegisters']])
            
            
            data_cash_cuth = CashCutModel(**data_json)
            response = create_cash_cut_register(data_cash_cuth)
            
            if response:
                print("Cash cut creado exitosamente")
                return 201, "Cash cut creado exitosamente"
            
            return 500, "Error creando el cash cut"
        except Exception as e:
            print(e)
            return 500, f"Error creando el cash cut: {str(e)}"
        
    def get_service_chosen(self, data_json: dict) -> tuple[int, Any]:
        """
        Función para obtener los servicios elegibles para un corte de caja.

        Valida los datos de entrada, excluye el servicio "agua" y filtra los servicios
        que ya han tenido un corte de caja para el año en curso.

        Args:
            data_json (dict): Un diccionario con 'DIM_ServiceDetailesType' (una lista) y 'DIM_service'.

        Returns:
            tuple[int, Any]: Una tupla con el código de estado y una lista de tuplas.
                             - 200 y una lista de tuplas con los IDs y nombres de los servicios elegibles.
                             - 400 si los datos de entrada son inválidos.
        """
        field_required = ['DIM_ServiceDetailesType', 'DIM_service']
        type_filed = [list , str]
        is_valid, message = validate_data(data_json, field_required, type_filed, "cash_cut")
        
        if not is_valid:
            return 400, []
        
        
        if data_json['DIM_service'] == "agua":
            return 200, []
        
        
        handler_date = DIM_DATE()
        date = handler_date.full_date
        
        services = []
        for dim_service_dails in data_json['DIM_ServiceDetailesType']: 
                
            dim_ServiceDailesId = get_service_detailsID(dim_service_dails, date[0], data_json['DIM_service'])
            
            if  is_service_exist(dim_ServiceDailesId): #Si existe ya, entonces no se cuenta
                continue
            
            
            #Verificar que el servicio sea valido
            if not search_service_Valid(date[0], dim_ServiceDailesId):
                continue
            
            services.append((dim_ServiceDailesId, dim_service_dails))
            
        
        return 200, services