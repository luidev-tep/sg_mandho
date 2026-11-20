from src.utils.conexion import Conexion, DatabaseError
from src.fact_revenues.models.fact_revenue import FACT_Revenue

def insert_fact_revenue(data_revenue: FACT_Revenue, db: Conexion | None = None) -> bool:
    """Inserta un nuevo registro de ingresos en la tabla FACT_Revenue.

    Esta función toma un objeto de datos de ingresos y lo inserta en la base
    de datos, manejando la conexión y el commit (o participando en una
    transacción compartida si se proporciona `db`).

    Args:
        data_revenue (FACT_Revenue): Objeto con los atributos necesarios para la inserción.
        db (Conexion | None): Conexión compartida opcional para transacciones atómicas.

    Returns:
        bool: Retorna True si la inserción fue exitosa y False en caso de error.
    """
    object_conetion = Conexion(shared_conn=db)
    try:
        query = """INSERT INTO FACT_Revenue (FACT_RevenueId, DIM_DateId, DIM_AccountId, DIM_ServiceDetailsId, DIM_MovementId, DIM_StatusId, amount)
            VALUES
        (?, ?, ?, ?, ?, ?, ?)"""
        
            # Impresión de la información de la tabla `data_revenue`
            # usando un f-string para formatear la salida.

        #print()
        string = f"""
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
    except DatabaseError as e:
        print(f"Error al insertar el pago: {str(e)}")
        return False
    finally:
        object_conetion.close_conexion()
        
def insert_many_fact_revenues(data_revenue: list[FACT_Revenue], db: Conexion | None = None) -> bool:
    """Inserta múltiples registros de ingresos en la tabla FACT_Revenue.

    Esta función toma una lista de objetos de datos de ingresos y los inserta
    en la base de datos de forma optimizada mediante `executemany`,
    manejando la conexión y el commit de la transacción.

    Args:
        data_revenue (list[FACT_Revenue]): Una lista de objetos `FACT_Revenue`
                                           que contienen los atributos necesarios para
                                           la inserción, como `Fact_RevenueId`, `DIM_DateId`, etc.
        db (Conexion | None): Conexión compartida opcional para transacciones atómicas.

    Returns:
        bool: Retorna True si todas las inserciones fueron exitosas y False en caso de error.
    """
    object_conetion = Conexion(shared_conn=db)
    try:
        # Consulta SQL para la inserción de múltiples registros
        query = """
        INSERT INTO FACT_Revenue (
            FACT_RevenueId, 
            DIM_DateId, 
            DIM_AccountId, 
            DIM_ServiceDetailsId, 
            DIM_MovementId, 
            DIM_StatusId, 
            amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Preparar todos los valores de los objetos en una lista de tuplas
        valores = [
            (
                revenue.Fact_RevenueId,
                revenue.DIM_DateId,
                revenue.DIM_AccountId,
                revenue.DIM_ServiceDetailsId,
                revenue.DIM_MovementId,
                revenue.DIM_StatusId,
                revenue.amount,
            )
            for revenue in data_revenue
        ]
        
        # Optimización fast_executemany para pyodbc en SQL Server
        object_conetion.cursor.fast_executemany = True
        # Ejecutar todas las inserciones en una sola operación optimizada
        object_conetion.cursor.executemany(query, valores)
        object_conetion.save_changes()
        
        return True
    except DatabaseError as e:
        # Captura errores específicos de base de datos e imprime el mensaje de error
        print(f"Error al insertar los registros: {str(e)}")
        return False
    finally:
        # Asegurar que la conexión a la base de datos se cierre correctamente
        object_conetion.close_conexion()
        
    # El siguiente bloque de código está comentado porque es un ejemplo de impresión
    # y no forma parte de la lógica funcional de la función.
    # print()
    # """
    # INFORMACIÓN DEL REGISTRO EN FACT_Revenue:
    # -----------------------------------------
    # ID de Factura Revenue:      {data_revenue.Fact_RevenueId}
    # ID de Fecha:                {data_revenue.DIM_DateId}
    # ID de Cuenta:               {data_revenue.DIM_AccountId}
    # ID de Detalle de Servicio:  {data_revenue.DIM_ServiceDetailsId}
    # ID de Movimiento:           {data_revenue.DIM_MovementId}
    # ID de Estado:               {data_revenue.DIM_StatusId}
    # Monto del Pago:             {data_revenue.amount}
    # -----------------------------------------
    # """