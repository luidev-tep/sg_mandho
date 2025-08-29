from src.utils.conexion import Conexion
from src.payments.model.vista_model import VistaModel
import sqlite3

def get_fact_revenues_by_customer_id(DIM_CustomerId: str, serviceName: str, service_type: str) -> tuple[int, list[dict]]:
    """
    Funcion para obtener los pagos que se realizaron en un solo anio para una persona, basado en el tipo de s
    servicio que se esta ingresando. se tienen que ingresar tanto su service name el nombre del servicio y tambien
    el tipo de servicio
    """
    handler_conexion = Conexion()
    handler_vista = VistaModel()
    query_base = f"""
        SELECT
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.StatusFactura,
        vw.amount,
        vw.FACT_RevenueId,
		vw.DIM_DateId,
        DIM_AccountId
		from VISTA_PAGOS_[tabla] as vw
		where DIM_CustomerId = ? AND
        vw.ServiceDetailesType = ?
        """
    try:
        quwery_base = query_base.replace("[tabla]", serviceName.upper())
        values = (DIM_CustomerId, service_type, )

        print(quwery_base , values)
        handler_conexion.cursor.execute(quwery_base, values)
        rows = handler_conexion.cursor.fetchall()

        if rows is None or not rows:
            return 200, []

        # Construimos los datos utilizando el modelo de vista
        datos = [handler_vista.Buid_vista_by_customer(*row) for row in rows if row]  # Usamos unpacking para pasar los valores

        return 200, datos

    except sqlite3.Error as e:
        # En caso de un error con la base de datos, retornamos un código 500 (Internal Server Error)
        print(f"Error de base de datos: {e}")
        return 500, []
    finally:
        # Aseguramos que la conexión se cierre
        handler_conexion.close_conexion()

