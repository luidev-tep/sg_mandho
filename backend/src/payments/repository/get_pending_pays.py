import sqlite3
from src.utils.conexion import Conexion
from src.payments.services.special_services import SpecialServices
from src.payments.model.pending_paid import PendingPaidModel, PendingPaidModel2


def get_query(type_transaction: str) -> str:
    """
    Genera consultas SQL dinámicas para obtener pagos pendientes basadas en el tipo de transacción.
    
    Utiliza Common Table Expressions (CTEs) para una lógica clara y modular que compara
    todos los servicios existentes contra los servicios ya pagados por un cliente específico.
    
    Args:
        type_transaction (str): Tipo de consulta a generar. Valores aceptados:
            - 'get_pending_pays': Consulta para un servicio específico
            - 'get_all_payments_pending': Consulta para todos los servicios
    
    Returns:
        str: Consulta SQL formateada según el tipo de transacción especificado
        
    Notes:
        La consulta base utiliza tres CTEs:
        1. TodosLosServicios: Lista completa de servicios que deberían existir
        2. PagosDelClienteEspecifico: Servicios que el cliente ya pagó
        3. SELECT final: Diferencia entre servicios existentes y pagados
    """
    Query_base = f"""
            -- Este bloque de consulta utiliza Common Table Expressions (CTE) para una lógica clara y modular.
            WITH
            -- 1. Obtenemos la lista completa de todos los servicios que deberían existir para un tipo de servicio.
            TodosLosServicios AS (
                SELECT
                    dat.FiscalYear,
                    svtype.DIM_ServiceDetailsId,
                    [nombre_servicio]
                    svtype.ServiceDetailesType,
                    svtype.amount
                FROM DIM_ServiceDetails AS svtype
                JOIN DIM_Service AS service ON service.DIM_ServiceId = svtype.DIM_ServiceId 
                JOIN DIM_Date AS dat ON svtype.DIM_DateId = dat.DIM_DateId
                -- Filtramos por el nombre del servicio para reducir el conjunto de datos inicial.
                [filtro_1]
            ),

            -- 2. Obtenemos una lista única de los servicios que el cliente ESPECÍFICO ya pagó.
            --    Esto se hace para filtrar los servicios que ya están liquidados.
            PagosDelClienteEspecifico AS (
                SELECT DISTINCT -- Usamos DISTINCT porque solo nos interesa saber si pagó, no cuántas veces.
                    FACT_Revenue.DIM_ServiceDetailsId
                FROM FACT_Revenue
                JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
                JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
                WHERE
                    -- Filtramos por el ID de la cuenta del cliente y el tipo de movimiento 'INGRESO'.
                    DIM_Account.DIM_CustomerId = ?
                    AND UPPER(DIM_Movement.MovementName) = 'INGRESO'
            )

            -- 3. Hacemos el SELECT final para encontrar la diferencia.
            --    Comparamos ambas tablas (TodosLosServicios vs. PagosDelClienteEspecifico)
            SELECT
                s.FiscalYear,
                [campo_adicional]
                s.ServiceDetailesType,
                s.amount
            FROM TodosLosServicios AS s
            -- Realizamos un LEFT JOIN para mantener todos los registros de 'TodosLosServicios'
            -- y buscar coincidencias en 'PagosDelClienteEspecifico'.
            LEFT JOIN PagosDelClienteEspecifico AS p
                ON s.DIM_ServiceDetailsId = p.DIM_ServiceDetailsId
            -- El truco final: nos quedamos solo con aquellos donde no hubo una coincidencia en los pagos.
            -- Si p.DIM_ServiceDetailsId es NULL, significa que ese servicio no estaba en la lista de pagos del cliente.
            WHERE
                p.DIM_ServiceDetailsId IS NULL
                ORDER by FiscalYear;
            """
    
    # Personalización de la consulta según el tipo de transacción
    if type_transaction == "get_pending_pays":
        Query_base = Query_base.replace('[nombre_servicio]' ,'service.ServiceName,')
        Query_base = Query_base.replace('[filtro_1]','WHERE service.ServiceName = ?')
        Query_base = Query_base.replace('[campo_adicional]','')
    
    if type_transaction == "get_all_payments_pending":
        Query_base = Query_base.replace('[nombre_servicio]' ,'service.ServiceName,')
        Query_base = Query_base.replace('[campo_adicional]', 's.ServiceName , ')
        Query_base = Query_base.replace('[filtro_1]', '')

    return Query_base 
    
    
def get_pending_pays(DIM_accountsId: int, serviceName: str) -> None | list[dict[str]] | list:
    """
    Obtiene los pagos pendientes de un servicio específico para una cuenta de cliente.
    
    Ejecuta una consulta SQL para identificar servicios que un cliente debería haber pagado
    pero aún no lo ha hecho, aplicando lógica especial para el servicio de agua.
    
    Args:
        DIM_accountsId (int): El ID de la cuenta del cliente para la cual se buscan los pagos pendientes
        serviceName (str): El nombre del servicio (ej: 'agua', 'feria', 'panteon')
    
    Returns:
        None | list[dict[str]] | list: 
            - Lista de diccionarios con la estructura [{'year': int, 'data': [{'serviceType': str, 'amount': float}]}]
            - Lista vacía [] si no hay pagos pendientes
            - None en caso de error de base de datos
    
    Examples:
        >>> get_pending_pays(123, 'agua')
        [
            {'year': 2022, 'data': [{'serviceType': 'tomas', 'amount': 360.0}]},
            {'year': 2023, 'data': [{'serviceType': 'consumo', 'amount': 360.0}]}
        ]
    ESTA CLASE SE MANDA A LLAMAR EN USUARIOS PARA PODER VER SUS PAGOS PENDIENTES
    """
    handler_conexion = Conexion()
    special_service = SpecialServices()
    try:
        query = get_query('get_pending_pays')
        handler_conexion.cursor.execute(query, (serviceName, DIM_accountsId))
        rows = handler_conexion.cursor.fetchall()
        
        # Verificación de resultados vacíos
        if not rows:
            return []
        
        # Aplicación de reglas especiales para el servicio de agua
        if serviceName == "agua":
            rows = special_service.is_already_paid(rows)

        # Conversión de resultados a formato de diccionario
        rows_format = [PendingPaidModel(*row).to_dict() for row in list(rows)]

        # Agrupamiento de resultados por año
        grouped_by_year = {}
        for row in rows_format:
            year = row['year']
            if year not in grouped_by_year:
                grouped_by_year[year] = []
            grouped_by_year[year].append({'serviceType': row['serviceType'], 'amount': row['amount']})

        # Formateo final de la respuesta
        response = [{'year': year, 'data': data} for year, data in grouped_by_year.items()]
        
        # Ordenamiento por año ascendente
        return sorted(response, key=lambda x: x['year'])
    except sqlite3.Error as e:
        print("""Error al obtener el ID del servicio: """, e)
        return None
    finally:
        handler_conexion.close_conexion()


def get_all_payments_pending(dim_customerId: int) -> list | None:
    """
    Obtiene TODOS los pagos pendientes de un cliente sin importar el servicio.
    
    Consulta todos los servicios pendientes de pago para un cliente, aplicando reglas especiales
    para el servicio de agua donde se requiere que ambos tipos (tomas y consumo) estén pendientes
    para mostrarse en los resultados.
    
    Args:
        dim_customerId (int): El ID del cliente para el cual se buscan todos los pagos pendientes
    
    Returns:
        list | None: 
            - Lista de diccionarios con estructura [{'year': int, 'data': [{'ServiceName': str, 'serviceType': str}]}]
            - None en caso de error de base de datos
    
    Raises:
        sqlite3.Error: Si ocurre un error en la consulta a la base de datos
    
    Notes:
        Para el servicio de agua, solo se muestran los servicios si ambos tipos (tomas y consumo)
        están pendientes. Si falta alguno, se eliminan todos los servicios de agua de ese año.
    """
    handler_conexion = Conexion()
    try:
        query = get_query('get_all_payments_pending')
        handler_conexion.cursor.execute(query, (dim_customerId,))
        rows = handler_conexion.cursor.fetchall()
        
        # Validación corregida para resultados vacíos
        if not rows:
            return []
        
        # Conversión de resultados a formato de diccionario
        rows_format = [PendingPaidModel2(*row).to_dict() for row in list(rows)]

        # Agrupamiento de resultados por año
        grouped_by_year = {}
        for row in rows_format:
            year = row['year']
            if year not in grouped_by_year:
                grouped_by_year[year] = []
            grouped_by_year[year].append({'ServiceName': row['ServiceName'], 'serviceType': row['serviceType']})

        # Procesamiento especial para servicios de agua
        for year, services in grouped_by_year.items():
            # Filtrado de servicios de agua
            water_services = [s for s in services if s['ServiceName'] == 'agua']
            water_types = {s['serviceType'] for s in water_services}
            
            # Eliminación de servicios de agua si no están ambos tipos requeridos
            if water_services and water_types != {'tomas', 'consumo'}:
                grouped_by_year[year] = [s for s in services if s['ServiceName'] != 'agua']

        # Formateo final de la respuesta
        response = [{'year': year, 'data': data} for year, data in grouped_by_year.items()]
        
        # Ordenamiento por año ascendente
        return sorted(response, key=lambda x: x['year'])
        
    except sqlite3.Error as e:
        """Manejo de errores de base de datos"""
        print(f"Error al obtener el ID del servicio: {e}")
        return None
    finally:
        """Cierre garantizado de la conexión a base de datos"""
        handler_conexion.close_conexion()