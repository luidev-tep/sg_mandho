from src.utils.conexion import Conexion
from src.fact_revenues.models.fact_revenue import FACT_Revenue
import sqlite3

def insert_fact_revenue(data_revenue: FACT_Revenue) -> bool:
    """Inserta un nuevo registro de ingresos en la tabla FACT_Revenue.

    Esta función toma un objeto de datos de ingresos y lo inserta en la base
    de datos, manejando la conexión y el commit.

    Args:
        data_revenue (object): Un objeto que contiene los atributos
                               necesarios para la inserción, como
                               Fact_RevenueId, DIM_DateId, etc.

    Returns:
        bool: Retorna True si la inserción fue exitosa y False en caso de error.
    """
    object_conetion = Conexion()
    try:
        query = """INSERT INTO FACT_Revenue (FACT_RevenueId, DIM_DateId, DIM_AccountId, DIM_ServiceDetailsId, DIM_MovementId, DIM_StatusId, amount)
            VALUES
        (?, ?, ?, ?, ?, ?, ?)"""
        
            # Impresión de la información de la tabla `data_revenue`
            # usando un f-string para formatear la salida.

        #print()
        f"""
        INFORMACIÓN DEL REGISTRO EN FACT_Revenue:
        -----------------------------------------
        ID de Factura Revenue:     {data_revenue.Fact_RevenueId}
        ID de Fecha:               {data_revenue.DIM_DateId}
        ID de Cuenta:              {data_revenue.DIM_AccountId}
        ID de Detalle de Servicio: {data_revenue.DIM_ServiceDetailsId}
        ID de Movimiento:          {data_revenue.DIM_MovementId}
        ID de Estado:              {data_revenue.DIM_StatusId}
        Monto del Pago:            {data_revenue.amount}
        -----------------------------------------
        """

        valores = (
            data_revenue.Fact_RevenueId,
            data_revenue.DIM_DateId,
            data_revenue.DIM_AccountId,
            data_revenue.DIM_ServiceDetailsId,
            data_revenue.DIM_MovementId,
            data_revenue.DIM_StatusId,
            data_revenue.amount,
        )
        object_conetion.cursor.execute(query, valores)
        object_conetion.save_changes()
        
        return True
    except sqlite3.Error as e:
        print(f"Error al insertar el pago: {str(e)}")
        return False
    finally:
        object_conetion.close_conexion()