from src.utils.conexion import Conexion
from src.payments.model.vista_model import VistaModel
import sqlite3

def get_query_base() -> str:
    """
    Construye la consulta SQL base para la vista de pagos.

    Esta función retorna una cadena de texto que contiene una consulta SELECT
    estándar para la vista de pagos, utilizando un placeholder `[tabla]`
    para ser reemplazado posteriormente con el nombre de servicio
    correspondiente.

    Returns:
        str: La cadena de consulta SQL base.
    """
    return f"""
        SELECT
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.StatusFactura,
        vw.amount,
        vw.DIM_DateId,
        DIM_AccountId
        from VISTA_PAGOS_DETALLADO_[tabla] as vw
        """

def get_fact_revenues_by_customer_id(DIM_CustomerId: str, serviceName: str, service_type: str, Year: str) -> tuple[int, list[dict]]:
    """
    Obtiene los pagos realizados por un cliente para un tipo de servicio específico.

    Esta función realiza una consulta a la base de datos para recuperar los
    detalles de los pagos (facturas) de un cliente, filtrando por su ID de
    cliente y el tipo de servicio. La tabla de la base de datos se determina
    dinámicamente a partir del nombre del servicio.

    Args:
        DIM_CustomerId (str): El ID único del cliente.
        serviceName (str): El nombre del servicio, utilizado para construir el
                           nombre de la tabla en la base de datos.
        service_type (str): El tipo de servicio (por ejemplo, 'mensual', 'anual').

    Returns:
        tuple[int, list[dict]]: Una tupla que contiene:
                                - Un código de estado (200 para éxito, 500 para error).
                                - Una lista de diccionarios, donde cada diccionario
                                  representa los datos de una factura. La lista
                                  estará vacía si no se encuentran resultados
                                  o si ocurre un error.

    Raises:
        sqlite3.Error: Si ocurre un error al interactuar con la base de datos SQLite.
    """
    handler_conexion = Conexion()
    handler_vista = VistaModel()
    query_base = get_query_base()
    query_base += f"""
        where vw.DIM_CustomerId = ? AND
        vw.ServiceDetailesType = ? AND
        vw.YearPay = ?
        """
    try:
        quwery_base = query_base.replace("[tabla]", serviceName.upper())
        values = (DIM_CustomerId, service_type, str(Year))

        #print(quwery_base , values)
        handler_conexion.cursor.execute(quwery_base, values)
        rows = handler_conexion.cursor.fetchall()

        if rows is None or not rows:
            return 200, []

        # Construimos los datos utilizando el modelo de vista
        datos = [handler_vista.Buid_vista_by_customer(*row, f'{row[-2]}{row[-1]}') for row in rows if row]  # Usamos unpacking para pasar los valores

        return 200, datos

    except sqlite3.Error as e:
        # En caso de un error con la base de datos, retornamos un código 500 (Internal Server Error)
        print(f"Error de base de datos: {e}")
        return 500, []
    finally:
        # Aseguramos que la conexión se cierre
        handler_conexion.close_conexion()