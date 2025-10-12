import sqlite3
from src.utils.conexion import Conexion
from src.payments.model.pending_paid import CashCutModel


def create_cash_cut_register(data_json: CashCutModel) -> bool:
    """
    Inserta un nuevo registro a la tabla DIM_cash cut.

    Args:
        data_json (CashCutModel): Objeto que contiene los datos a insertar.

    Returns:
        bool: True si el registro se insertó correctamente, False en caso de error.
    """
    handler = Conexion()
    query  = """
    INSERT INTO DIM_CashCut (DIM_CashCutId, DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceOwnersId, DIM_CountRegisters)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        values = (
            data_json.DIM_CashCutId,
            data_json.DIM_ServiceDetailsId,
            data_json.DIM_DateId,
            data_json.DIM_ServiceOwnersId,
            data_json.DIM_CountRegisters
        )
        handler.cursor.execute(query, values)
        handler.save_changes()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        handler.close_conexion()
        

def found_pending(DIM_ServiceDetailesType:str, ServiceName: str) -> list:
    """
    Función encargada de recopilar las cuentas de usuarios a los que se les
    creará un registro de pago con 0 para contabilizar los pagos pendientes.
    Solo se pueden hacer cortes de caja en el año actual para no afectar registros anteriores.

    Args:
        DIM_ServiceDetailesType (str): El tipo de detalle del servicio.
        ServiceName (str): El nombre del servicio.

    Returns:
        list: Una lista de tuplas con los DIM_AccountId de los clientes pendientes.
              Devuelve una lista vacía en caso de no encontrar resultados o si ocurre un error.
    """
    handler = Conexion()
    query  = """
             SELECT 
                 vw.DIM_AccountId
             FROM VISTA_CLIENTES_ACTIVOS as vw 
             WHERE vw.DIM_AccountId NOT IN (
                 SELECT 
                     fa.DIM_AccountId
                 FROM FACT_Revenue as fa
                 JOIN DIM_ServiceDetails as sd
                 ON sd.DIM_ServiceDetailsId = fa.DIM_ServiceDetailsId
                 JOIN DIM_Service as s
                 ON s.DIM_ServiceId = sd.DIM_ServiceId
                 WHERE s.ServiceName = ? AND sd.ServiceDetailesType = ?
             );
    """
    try:
        handler.cursor.execute(query, (ServiceName, DIM_ServiceDetailesType))
        result = handler.cursor.fetchall()
        
        if result is None or len(result) == 0:
            return []
        
        return result
    except sqlite3.Error as e:
        print(e)
        return []
    finally:
        handler.close_conexion()
        
    
def search_service_Valid(year: int, service_details_id: str) -> bool:
    """
    Busca si un servicio es válido para el año dado.
    Un servicio es válido si aún no se ha realizado un corte de caja para él.
    Solo se puede validar el año actual.

    Args:
        year (int): Año para el cual se busca el servicio.
        service_details_id (str): ID del servicio.

    Returns:
        bool: True si el servicio es válido para el año, False en caso contrario.
    """
    
    handler = Conexion()
    
    #print(f"year: {year}, service_details_id: {service_details_id}")
    query = """
    SELECT 
        DIM_StatusId     
    from DIM_ServiceDetails 
    JOIN DIM_Date as d on
        DIM_ServiceDetails.DIM_DateId = d.DIM_DateId
        AND d.Year = ?
    WHERE DIM_ServiceDetailsId = ?
    """
    try:
        handler.cursor.execute(query, (year, service_details_id))
        result = handler.cursor.fetchone()
        
        if result is None:
            return False
        
        if result[0] == 'status8' or result[0] == 'status6':
            return True
        
        return False
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        handler.close_conexion()
        
        
def is_service_exist(service_details_id: str) -> bool:
    """
    Verifica si ya existe un registro de corte de caja para un servicio.
    Si se encuentra un registro, significa que ya se ha realizado el corte de caja,
    por lo que la función retorna True.

    Args:
        service_details_id (str): ID del detalle del servicio.

    Returns:
        bool: True si el servicio ya tiene un corte de caja, False en caso contrario.
    """
    handler = Conexion()
    query = """
    --El service Detailes es unico por loq ue no se peude repetir ,se tiene la certenaza que no se repetira
        SELECT
        DIM_ServiceDetailsId
    FROM DIM_CashCut
    
    WHERE DIM_ServiceDetailsId = ?
    """
    try:
        handler.cursor.execute(query, (service_details_id,))
        result = handler.cursor.fetchone()
        
        if result is None: #Significa  que no existe ningun registro en la tabla, o que no se ha hecho corte de caja aun
            return False
        
        #print(result)
        return True
    except sqlite3.Error as e:
        print(e)
        # Si hay un error, asumimos que no se pudo verificar la existencia,
        # lo que en este contexto significa que no se puede proceder.
        return True 
    finally:
        handler.close_conexion()