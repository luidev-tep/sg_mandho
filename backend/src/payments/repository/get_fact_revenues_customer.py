from src.utils.conexion import Conexion, DatabaseError
from src.payments.model.vista_model import VistaModel

ALLOWED_SERVICES = {"agua", "feria", "panteon", "delegacion"}


def get_fact_revenues_by_customer_id(
    DIM_CustomerId: str,
    serviceName: str,
    service_type: str,
    Year: str,
    db: Conexion | None = None,
) -> tuple[int, list[dict]]:
    """
    Obtiene los pagos realizados por un cliente para un tipo de servicio y año específicos.

    Valida `serviceName` contra una lista blanca de servicios permitidos y consulta
    directamente `FACT_Revenue` con parámetros preparados (sin interpolación SQL)
    para retornar los montos individuales y los IDs reales `FACT_RevenueId`.

    Args:
        DIM_CustomerId (str): El ID único del cliente.
        serviceName (str): El nombre del servicio ('agua', 'feria', 'panteon', 'delegacion').
        service_type (str): El tipo de detalle del servicio.
        Year (str): El año del servicio/pago.
        db (Conexion | None): Conexión compartida opcional para participar en transacciones.

    Returns:
        tuple[int, list[dict]]: Código HTTP (200, 400, 500) y lista de diccionarios de facturas.
    """
    normalized_service = (serviceName or "").strip().lower()
    if normalized_service not in ALLOWED_SERVICES:
        return 400, []

    handler_vista = VistaModel()
    query = """
        SELECT
            c.CustomerName,
            c.CustomerMiddleName,
            c.CustomerLastName,
            c.CustomerSecondLastName,
            st.StatusName AS StatusFactura,
            fr.amount,
            fr.DIM_DateId,
            fr.DIM_AccountId,
            fr.FACT_RevenueId
        FROM FACT_Revenue AS fr
        INNER JOIN DIM_Account AS acc ON acc.DIM_AccountId = fr.DIM_AccountId
        INNER JOIN DIM_Customer AS c ON c.DIM_CustomerId = acc.DIM_CustomerId
        INNER JOIN DIM_ServiceDetails AS sd ON sd.DIM_ServiceDetailsId = fr.DIM_ServiceDetailsId
        INNER JOIN DIM_Service AS s ON s.DIM_ServiceId = sd.DIM_ServiceId
        INNER JOIN DIM_Date AS d_sd ON d_sd.DIM_DateId = sd.DIM_DateId
        INNER JOIN DIM_Status AS st ON st.DIM_StatusId = fr.DIM_StatusId
        INNER JOIN DIM_Movement AS m ON m.DIM_MovementId = fr.DIM_MovementId
        WHERE c.DIM_CustomerId = ?
          AND LOWER(s.ServiceName) = ?
          AND sd.ServiceDetailesType = ?
          AND CAST(d_sd.[Year] AS NVARCHAR(10)) = ?
          AND UPPER(m.MovementName) = N'INGRESO'
        ORDER BY fr.DIM_DateId ASC, fr.FACT_RevenueId ASC
    """

    handler_conexion = Conexion(shared_conn=db)
    try:
        values = (DIM_CustomerId, normalized_service, service_type, str(Year))
        handler_conexion.cursor.execute(query, values)
        rows = handler_conexion.cursor.fetchall()

        if not rows:
            return 200, []

        datos = [handler_vista.Buid_vista_by_customer(*row) for row in rows if row]
        return 200, datos

    except DatabaseError as e:
        print(f"Error de base de datos: {e}")
        return 500, []
    finally:
        handler_conexion.close_conexion()
