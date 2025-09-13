import sqlite3
from src.utils.conexion import Conexion

from src.payments.services.special_services import SpecialServices

from src.payments.model.pending_paid import PendingPaidModel
def get_pending_pays(DIM_accountsId, serviceName) -> None | list[dict[str]] | list:
    """
    Obtiene los pagos pendientes de un servicio específico para una cuenta de cliente.

    Esta función ejecuta una consulta SQL para identificar los servicios que un cliente debería
    haber pagado, pero aún no lo ha hecho. La lógica se basa en comparar una lista de todos los
    servicios existentes con la lista de los servicios que el cliente ya ha pagado.

    Args:
        DIM_accountsId (int): El ID de la cuenta del cliente para la cual se buscan los pagos pendientes.
        serviceName (str): El nombre del servicio (por ejemplo, 'agua', 'luz', 'internet').

    Returns:
        None | list[dict[str]] | list: Una lista de diccionarios, donde cada diccionario representa un año
        y contiene una lista de los servicios pendientes para ese año. Si no hay pagos pendientes
        o si ocurre un error, retorna una lista vacía o None.
        
        El formato de la salida es el siguiente:
        [
            {'year': 2022,
             'data': [
                {'serviceType': 'tomas', 'amount': 360.0},
                {'serviceType': 'consumo', 'amount': 360.0}
             ]
            }, 
            {'year': 2023, 
             'data': [{'serviceType': 'tomas', 'amount': 360.0}, {'serviceType': 'consumo', 'amount': 360.0}]
            }
        ]
    """
    handler_conexion = Conexion()
    special_service = SpecialServices()
    try:
        query = f"""
            -- Este bloque de consulta utiliza Common Table Expressions (CTE) para una lógica clara y modular.
            WITH
            -- 1. Obtenemos la lista completa de todos los servicios que deberían existir para un tipo de servicio.
            TodosLosServicios AS (
                SELECT
                    dat.FiscalYear,
                    svtype.DIM_ServiceDetailsId,
                    service.ServiceName,
                    svtype.ServiceDetailesType,
                    svtype.amount
                FROM DIM_ServiceDetails AS svtype
                JOIN DIM_Service AS service ON service.DIM_ServiceId = svtype.DIM_ServiceId 
                JOIN DIM_Date AS dat ON svtype.DIM_DateId = dat.DIM_DateId
                -- Filtramos por el nombre del servicio para reducir el conjunto de datos inicial.
                WHERE service.ServiceName = ?
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
        # Ejecutamos la consulta con los parámetros de forma segura.
        handler_conexion.cursor.execute(query, (serviceName, DIM_accountsId))
        rows = handler_conexion.cursor.fetchall()
        
        if rows[0] is None:
            return None
        
        # Filtramos los pagos si el servicio es 'agua', ya que solo se necesita un pago anual.
        if serviceName == "agua":
            rows = special_service.is_already_paid(rows)

        # Convertimos los resultados de la consulta a un formato de diccionario usando un modelo.
        rows_format = [PendingPaidModel(*row).to_dict() for row in list(rows)]

        # Agrupamos los resultados por año para la estructura de salida deseada.
        grouped_by_year = {}
        for row in rows_format:
            year = row['year']
            if year not in grouped_by_year:
                grouped_by_year[year] = []
            grouped_by_year[year].append({'serviceType': row['serviceType'], 'amount': row['amount']})

        # Damos formato final a la respuesta como una lista de diccionarios.
        response = [{'year': year, 'data': data} for year, data in grouped_by_year.items()]
        # Ordenamos la respuesta por año.
        return sorted(response, key=lambda x: x['year'])
    except sqlite3.Error as e:
        # Manejo de errores en caso de problemas con la base de datos.
        print(f"Error al obtener el ID del servicio: {e}")
        return []
    finally:
        # Nos aseguramos de cerrar la conexión a la base de datos.
        handler_conexion.close_conexion()