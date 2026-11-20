from src.utils.conexion import Conexion, DatabaseError
from src.payments.model.pending_paid import CashCutModel


def create_cash_cut_register(data_json: CashCutModel, db: Conexion | None = None) -> bool:
    """
    Inserta un nuevo registro a la tabla DIM_cash cut.

    Args:
        data_json (CashCutModel): Objeto que contiene los datos a insertar.
        db (Conexion | None): Conexión compartida para transacciones atómicas.

    Returns:
        bool: True si el registro se insertó correctamente, False en caso de error.
    """
    handler = Conexion(shared_conn=db)
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
    except DatabaseError as e:
        print(e)
        return False
    finally:
        handler.close_conexion()
        

def found_pending(
    DIM_ServiceDetailesType: str,
    ServiceName: str,
    service_details_id: str | None = None,
) -> list:
    """
    Recopila las cuentas activas a las que aún no se les ha registrado ningún pago
    para el detalle de servicio indicado.

    Usa `NOT EXISTS` (inmune a `NULL` en `FACT_Revenue.DIM_AccountId`) y filtra
    por `DIM_ServiceDetailsId` cuando se proporciona (o por servicio/tipo/año actual).

    Args:
        DIM_ServiceDetailesType (str): El tipo de detalle del servicio.
        ServiceName (str): El nombre del servicio.
        service_details_id (str | None): ID específico de `DIM_ServiceDetails` del año en curso.

    Returns:
        list: Lista de tuplas `(DIM_AccountId,)` de cuentas pendientes.
    """
    handler = Conexion()
    if service_details_id:
        query = """
            SELECT vw.DIM_AccountId
            FROM VISTA_CLIENTES_ACTIVOS AS vw
            WHERE NOT EXISTS (
                SELECT 1
                FROM FACT_Revenue AS fa
                WHERE fa.DIM_AccountId = vw.DIM_AccountId
                  AND fa.DIM_ServiceDetailsId = ?
            );
        """
        params = (service_details_id,)
    else:
        query = """
            SELECT vw.DIM_AccountId
            FROM VISTA_CLIENTES_ACTIVOS AS vw
            WHERE NOT EXISTS (
                SELECT 1
                FROM FACT_Revenue AS fa
                INNER JOIN DIM_ServiceDetails AS sd
                    ON sd.DIM_ServiceDetailsId = fa.DIM_ServiceDetailsId
                INNER JOIN DIM_Service AS s
                    ON s.DIM_ServiceId = sd.DIM_ServiceId
                INNER JOIN DIM_Date AS d_sd
                    ON d_sd.DIM_DateId = sd.DIM_DateId
                WHERE fa.DIM_AccountId = vw.DIM_AccountId
                  AND s.ServiceName = ?
                  AND sd.ServiceDetailesType = ?
                  AND d_sd.[Year] = YEAR(GETDATE())
            );
        """
        params = (ServiceName, DIM_ServiceDetailesType)

    try:
        handler.cursor.execute(query, params)
        result = handler.cursor.fetchall()

        if not result:
            return []

        return result
    except DatabaseError as e:
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
    except DatabaseError as e:
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
    except DatabaseError as e:
        print(e)
        # Si hay un error, asumimos que no se pudo verificar la existencia,
        # lo que en este contexto significa que no se puede proceder.
        return True 
    finally:
        handler.close_conexion()