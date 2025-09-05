from typing import Literal
from src.fact_revenues.services.service import get_status_payment
from src.fact_revenues.models.fact_revenue import FACT_Revenue
from src.utils.id_generator import create_id
from src.dim_dates.dim_date import DIM_DATE

#importacion para obtener el estado del pago
from src.dim_status.status import DIM_status

#importacion para la validacion de cantidad
from src.fact_revenues.services.service import valide_amount, get_status_payment_for_registers

from src.fact_revenues.repository.insert import insert_fact_revenue
# Importacion del handler de movimiento
from src.dim_movement.DIM_movent import DIM_Movement

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
        
        # Aunque las funciones hacen lo mismo, para evitar errores inesperados se separan
        if data_json['entrada'] == 'crear_pago':
            statusName = get_status_payment(data_json['amount'], data_json['FactAmount'])
        else:
            #Ya se encarga internamente de actualizar todos los registros como pagados,
            params = [data_json['amount'], data_json['FactAmount'], data_json['DIM_CustomerId'],data_json['serviceDetailsType'],  data_json['ServiceName'], data_json['AnioPago'],]
            statusName = get_status_payment_for_registers(*params)
            

        estatus_id = handler_status.get_status_id(statusName, "fact_revenue")
        dim_date_data = DIM_DATE()
        #Validar como se debe guardar el pago
        print(f"Datos del diccionario json", data_json)
        data_format = {
            'FACT_RevenueId': create_id([data_json['FactAmount'], data_json['DIM_AccountId'], dim_date_data.dateId]), #Asi se evita que el id se repita
            'DIM_DateId': dim_date_data.dateId,
            'DIM_AccountId': data_json['DIM_AccountId'],
            'DIM_ServiceDetailsId': data_json['DIM_ServiceDetailsId'],
            'DIM_MovementId': handler_movement.get_movement_id(data_json['movementName']),
            'DIM_StatusId': estatus_id,
            'amount': data_json['FactAmount'],
        }
        
        fact_register = FACT_Revenue(**data_format)
        revenuer = fact_register.to_dict()

        for key, value in revenuer.items():
            print(f"{key}: {value}")

        isvalid = insert_fact_revenue(fact_register)

        if not isvalid:
            return 500, "Error creando el pago"
        
        return 201, "Pago creado exitosamente"