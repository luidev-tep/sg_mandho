from typing import Literal, Any, LiteralString
import sqlite3
from src.utils.conexion import Conexion
from src.payments.repository.read_payments import ReadPayment
#from src.dim_servicedetails.repository.show import get_count_servicetypes_by_service
from src.dim_service.DIM_Service import DIM_Service

#Inicaliza la clase de servicio 
handler_service = DIM_Service()
class ValidatePayment():
    """
    Clase para validar la existencia de pagos duplicados o conflictivos en el sistema.
    Proporciona métodos para verificar si un cliente ya tiene pagos registrados
    para un servicio específico en un año determinado, considerando diferentes
    escenarios como pagos pendientes y el origen de la solicitud.
    """

    def is_payment_active(self, DIM_CustomerId, AnioPago, ServiceName, input, serviceDetailstype) -> tuple[Literal[True], Literal['']] | tuple[Literal[False], LiteralString]:
        """
            Valida si un cliente ya tiene un pago registrado para un servicio en un año específico.
    
    Esta función es crucial para prevenir pagos duplicados. Considera tanto el estado
    de los pagos existentes (pendiente/completado) como el origen de la solicitud
    (crear_pago/terminar_pago) para determinar si se permite o no un nuevo pago.
    
    Parámetros:
        DIM_CustomerId (int): Identificador único del cliente en el sistema DIM
        AnioPago (int): Año para el cual se está verificando la existencia de pagos
        ServiceName (str): Nombre del servicio a validar (ej: 'agua', 'panteon')
        input (str): Origen de la solicitud ('crear_pago' o 'terminar_pago')
        serviceDetailstype (str): Tipo específico de servicio para casos donde 
                                 un servicio puede tener múltiples variantes
    
    Retorna:
        tuple: Tupla con dos elementos:
            - bool: True si se permite el pago, False si existe conflicto
            - str: Mensaje vacío si no hay error, mensaje de error en caso contrario
    
    Ejemplo:
        >>> validator = ValidatePayment()
        >>> resultado, mensaje = validator.is_another_payment_in_year(
        ...     12345, 2023, 'agua', 'crear_pago', 'residencial'
        ... )
        """
        class_vista = ReadPayment()
        
        # Construcción de query según el tipo de servicio
        if ServiceName == 'agua':
            query = "where DIM_CustomerId = ? AND YearPay = ?"
            values = (DIM_CustomerId, AnioPago)
        else:
            query = "where DIM_CustomerId = ? AND YearPay = ? AND ServiceDetailesType = ?"
            values = (DIM_CustomerId, AnioPago, serviceDetailstype)

        registros = class_vista.get_validation_payment(ServiceName, query, values)
        #print(registros)
        # Si no hay registros, permitir el pago
        if registros is None or len(registros) == 0:
            return True, ''
        
        # Verificar si existe algún pago que NO esté pendiente
        for registro in registros:
            #print(registro)
            if registro[6] != 'pendiente':
                return False, 'El cliente ya tiene un pago para este servicio en este anio'
        
        # Si todos los pagos están pendientes, verificar el origen de la solicitud
        if input == 'crear_pago':
            return False, 'El cliente ya tiene un pago pendiente para este servicio en este anio'
        else:
            return True, ''
        
    def is_account_active(self, DIM_accountId) -> bool: 
        """
        Verifica que la cuenta no sea de tipo estudiante o de tipo invalido, ya que los estudiantes no pueden 
        realizar pagos y las cuentas invalidas no pueden realizar pagos.
        Se han agregado otros 2 nuevos campos, los cuale sosn residente y vecino exento, ya que estos no pueden 
        realizar pagos.
        """
        handler_coneccion = Conexion()
        query = """
            SELECT d.RoleName from DIM_Account as a, DIM_Role as d
            WHERE a.DIM_RoleId = d.DIM_RoleId
            and DIM_AccountId = ?
        """

        handler_coneccion.cursor.execute(query, (DIM_accountId,))
        result = handler_coneccion.cursor.fetchone()
        if result is None:
            return False
        elif result[0] in ['estudiante', 'invalido', 'vecino exento', 'residente']:
            return False
        else:
            return True
