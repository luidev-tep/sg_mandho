from src.utils.conexion import Conexion
from typing import Literal
import random
import uuid
from src.fact_revenues.services.service import get_status_payment
from src.fact_revenues.models.fact_revenue import FACT_Revenue
from src.utils.id_generator import create_id
from src.dim_dates.dim_date import DIM_DATE

#importacion para obtener el estado del pago
from src.dim_status.status import DIM_status

#importacion para la validacion de cantidad
from src.fact_revenues.services.service import valide_amount, get_status_payment_for_registers

from src.fact_revenues.repository.insert import insert_fact_revenue, insert_many_fact_revenues
# Importacion del handler de movimiento
from src.dim_movement.DIM_movent import DIM_Movement

# Se importa la funcion para obtener el id de detalles del servicio
from src.dim_servicedetails.repository.show import get_service_detailsID, get_amount_by_id  

from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud
hanlder_service_details = ServiceDetailsCrud()
handler_movement = DIM_Movement()
handler_status = DIM_status()


class factRevenueCrud():
    def create_fact_revenue(self, data_json: dict) -> tuple[Literal[500], Literal['Error creating payment']] | tuple[Literal[201], Literal['Payment created successfully']]:
        """
        Crea un nuevo pago en la base de datos.

        Esta función valida la cantidad del pago, determina su estado,
        y luego construye y registra el objeto de pago en la base de datos.

        Args:
            data_json (dict): Un diccionario que contiene la información del pago,
                             incluyendo 'amount', 'DIM_ServiceDetailsId', 'DIM_AccountId',
                             'FactAmount', y 'movementName'.

        Returns:
            tuple[Literal[500], Literal['Error creating payment']] | tuple[Literal[201], Literal['Payment created successfully']]:
                Una tupla con un código de estado y un mensaje descriptivo.
                - (400, "La cantidad registrada no coincide con la del servicio") si la cantidad no es válida.
                - (500, "Error creating payment") si falla la inserción en la base de datos.
                - (201, "Payment created successfully") si el pago se crea correctamente.
        """
        isvalid = valide_amount(data_json['amount'], data_json['DIM_ServiceDetailsId'])

        if not isvalid:
            return 400, "La cantidad registrada no coincide con la del servicio"

        dim_date_data = DIM_DATE()
        movement_id = handler_movement.get_movement_id(data_json['movementName'])
        completo_status_id = handler_status.get_status_id("completo", "fact_revenue")
        pendiente_status_id = handler_status.get_status_id("pendiente", "fact_revenue")
        status_map = {
            "completo": completo_status_id,
            "pendiente": pendiente_status_id,
        }
        fact_revenue_id = f"rev-{uuid.uuid4().hex[:14]}"

        if data_json['entrada'] == 'crear_pago':
            statusName = get_status_payment(data_json['amount'], data_json['FactAmount'])
            if not statusName:
                return 400, "El monto recibido excede el costo del servicio"

            estatus_id = status_map.get(statusName) or handler_status.get_status_id(statusName, "fact_revenue")
            if not estatus_id:
                return 500, f"No se pudo obtener el esto de pago, {statusName}"

            data_format = {
                'FACT_RevenueId': fact_revenue_id,
                'DIM_DateId': dim_date_data.dateId,
                'DIM_AccountId': data_json['DIM_AccountId'],
                'DIM_ServiceDetailsId': data_json['DIM_ServiceDetailsId'],
                'DIM_MovementId': movement_id,
                'DIM_StatusId': estatus_id,
                'amount': data_json['FactAmount'],
            }
            fact_register = FACT_Revenue(**data_format)
            isvalid = insert_fact_revenue(fact_register)
            if not isvalid:
                return 500, "Error creando el pago"
            return 201, "Pago creado exitosamente"

        params = [
            data_json['amount'],
            data_json['FactAmount'],
            data_json['DIM_CustomerId'],
            data_json['serviceDetailsType'],
            data_json['ServiceName'],
            data_json['AnioPago'],
        ]
        with Conexion() as tx:
            statusName = get_status_payment_for_registers(
                *params,
                db=tx,
                completo_status_id=completo_status_id,
            )
            if not statusName:
                tx.rollback()
                return 400, "El monto recibido excede el saldo pendiente del servicio"

            estatus_id = status_map.get(statusName)
            if not estatus_id:
                tx.rollback()
                return 500, f"No se pudo obtener el esto de pago, {statusName}"

            data_format = {
                'FACT_RevenueId': fact_revenue_id,
                'DIM_DateId': dim_date_data.dateId,
                'DIM_AccountId': data_json['DIM_AccountId'],
                'DIM_ServiceDetailsId': data_json['DIM_ServiceDetailsId'],
                'DIM_MovementId': movement_id,
                'DIM_StatusId': estatus_id,
                'amount': data_json['FactAmount'],
            }
            fact_register = FACT_Revenue(**data_format)
            isvalid = insert_fact_revenue(fact_register, db=tx)
            if not isvalid:
                tx.rollback()
                return 500, "Error creando el pago"

            tx.save_changes()
            return 201, "Pago creado exitosamente"
    
    def insert_many_register(self, data_format: list, ServiceDetailesId: str | None = None) -> tuple[int, str]:
        """
        Inserta una lista de pagos formateados y validados en la base de datos de forma atómica.

        Esta función procesa una lista de diccionarios de datos de pago, crea
        registros de tipo 'trabajado' y los inserta en la tabla `fact_revenues`.
        También actualiza el estado del servicio asociado a 'status8' en una única transacción.

        Args:
            data_format (list): Una lista de diccionarios, donde cada diccionario
                                representa un pago a ser insertado.
            ServiceDetailesId (str | None): ID opcional del detalle del servicio.

        Returns:
            tuple[int, str]: Código de estado y mensaje descriptivo.
        """
        try:
            # Obtener el ID del detalle del servicio
            test_data = data_format[0]
            dim_service_detail_id = ServiceDetailesId if ServiceDetailesId else get_service_detailsID(test_data['serviceDetailsType'], test_data["AnioPago"], test_data['ServiceName'])
            
            # Si el ID del servicio no existe, retornar un error
            if not dim_service_detail_id:
                return 400, f"serviceDetailsType '{test_data.get('serviceDetailsType', '')}' no se encontró."
            
            # Obtener el monto asociado al servicio
            amount = get_amount_by_id(dim_service_detail_id)
            
            # Obtener la fecha actual para el registro
            dim_date_data = DIM_DATE()
            year = str(dim_date_data.dateId)
            
            # Obtener el ID del estado 'trabajado'
            estatus_id = handler_status.get_status_id("trabajado", "fact_revenue")
            
            # Obtener el ID del movimiento 'ingreso'
            movement_id = handler_movement.get_movement_id(test_data['movementName'])
            
            model_format = []
            for data_json in data_format:
                index1 = random.randint(0, 15)
                index2 = random.randint(0, 15)
                index3 = random.randint(0, 15)
                extract = create_id([data_json['DIM_AccountId'][index1:], data_json['DIM_AccountId'][index2:], data_json['DIM_AccountId'][index3:]])
                extrat2 = create_id([dim_service_detail_id[index1:], dim_service_detail_id[index2:], dim_service_detail_id[index3:]])
                new_id = create_id([extract, extrat2, year[4:]])
                
                # Formatear los datos para el modelo de la base de datos
                formatted_data = {
                    'FACT_RevenueId': new_id,
                    'DIM_DateId': dim_date_data.dateId,
                    'DIM_AccountId': data_json['DIM_AccountId'],
                    'DIM_ServiceDetailsId': dim_service_detail_id,
                    'DIM_MovementId': movement_id,
                    'DIM_StatusId': estatus_id,
                    'amount': amount,
                }
                
                model_format.append(FACT_Revenue(**formatted_data))
            
            # Transacción atómica (Flujo C de la SPEC §3.3)
            with Conexion() as tx:
                isvalid = insert_many_fact_revenues(model_format, db=tx)
                if not isvalid:
                    tx.rollback()
                    return 500, "Error al insertar las facturas"
                
                status, mensaje = hanlder_service_details.Update_dim_service_details(dim_service_detail_id, 'status8', db=tx)
                if status != 200:
                    tx.rollback()
                    mensaje += " en el servicio " + test_data.get('ServiceName', '')
                    return status, mensaje
                
                tx.save_changes()
                return 201, "Pagos creados exitosamente"
        
        except Exception as e:
            print(e)
            return 500, "Error creando los pagos"