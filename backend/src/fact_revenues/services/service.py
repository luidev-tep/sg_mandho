import string
from src.dim_servicedetails.repository.show import get_amount_by_id

#Importacion de la funcion para actualizar una seria de registros, (Ver si convertir a una clase apra que solamente se acceda a sus metodos)
from src.fact_revenues.repository.edit import EditFactRevenue
handler_edit = EditFactRevenue()

#Obtener la funcion que recibe todos los pagos sociados a un solo cliente
from src.payments.repository.get_fact_revenues_customer import get_fact_revenues_by_customer_id

#importacion para obtener el estado del pago
from src.dim_status.status import DIM_status
hanlder_status = DIM_status()


from src.payments.repository.read_payments import ReadPayment
hanlder_querys = ReadPayment()
def get_status_payment(cost_service: float, amount: float) -> str:
    """Determina el estado de pago de un servicio.

    Compara el costo total del servicio con el monto pagado para definir
    el estado. Si el monto pagado es igual al costo, el estado es "pagado".
    Si el monto pagado es menor, el estado es "pendiente".

    Args:
        cost_service (float): El costo total del servicio.
        amount (float): El monto que se ha pagado por el servicio.

    Returns:
        str: Retorna "pagado" si el monto coincide, o "pendiente" si el
             monto es menor al costo del servicio.
    """
    estado = cost_service - amount
    if estado == 0:
        data = "completo"
    elif estado > 0:
        data = "pendiente"
    
    return data


def valide_amount(amount: float, id_amount: str) -> bool:
    """Valida si un monto recibido coincide con el valor registrado en la base de datos.

    Utiliza el ID de un servicio para buscar su monto correspondiente en la base de datos
    y lo compara con el monto proporcionado.

    Args:
        amount (float): El monto a validar.
        id_amount (str): El ID del detalle del servicio a consultar en la base de datos.

    Returns:
        bool: Retorna True si el monto coincide, o False si no hay coincidencia
              o si no se encuentra el ID en la base de datos.
    """
    amount_table = get_amount_by_id(id_amount)

    #print(f"amount_table en fact_revenues: {amount_table}, cantidad: {amount}")
    if not amount_table:
        return False
    
    return amount_table == amount


def get_status_payment_for_registers(
        cost_service: float,
        cantidad_recibida: float, 
        dim_customer_id: str, 
        servicedetails: str, 
        service_name: str, 
        year_pay: str) -> str:
    """Determina el estado de pago de un servicio y actualiza los registros asociados.

    Compara el costo total del servicio con la suma de todos los montos pagados
    para definir el estado. Si la suma total de pagos es igual o mayor al costo,
    el estado es "pagado" y se actualizan los registros correspondientes en la
    base de datos. Si la suma es menor, el estado es "pendiente".

    Args:
        cost_service (float): El costo total del servicio.
        cantidad_recibida (float): El monto del pago actual.
        dim_customer_id (str): El ID del cliente.
        servicedetails (str): Detalles del servicio.
        service_name (str): El nombre del servicio.
        year_pay (str): El año del pago.

    Returns:
        str: Retorna "pagado" si el monto total coincide o lo supera, o "pendiente" si es menor.
    """
    string =f"""
    DETALLE DE VALORES DE ENTRADA:
    -------------------------------
    Costo del Servicio:        {cost_service}
    Cantidad Recibida:         {cantidad_recibida}
    ID del Cliente:            {dim_customer_id}
    Tipo de Detalle de Servicio: {servicedetails}
    Nombre del Servicio:       {service_name}
    Año de Pago:               {year_pay}
    -------------------------------
    """
    #Obtener primero la suma de los pagos que lleva hasta ahora le cliente
    #Se actualizaran todos los pagos asociados a esta cuenta para que se marquen como pagados,
    status,registros_cliente = get_fact_revenues_by_customer_id(dim_customer_id, service_name, servicedetails, year_pay )

    if status != 200:
        print(f"Error al leer los pagos: {registros_cliente}")
        return ""
    #print("Se obtuvieron los pagos", len(registros_cliente))

    amount = cantidad_recibida
    for registro in registros_cliente:
        #print('Se imprime desde service.Get_ status payments for registers ')
        #print(registro)
        amount += registro['amount']
        
    estado = cost_service - amount
    data = ""
    if estado == 0:
        data = "completo"
        
        
        #Obtenemos el id de cada cuenta obtenida
        id_registros = [registro['FACT_RevenueId'] for registro in registros_cliente]
        #Para esto ya se debe saber el nombre de la columna que se quiere actualizar
        DIM_StatusId = hanlder_status.get_status_id(data, 'fact_revenues')
        handler_edit.update_many_registers(id_registros, 'DIM_StatusId', DIM_StatusId )

    elif estado > 0:
        data = "pendiente"
        
    else:
        print("No se le asigno ningun valor a la variable data")
    return data