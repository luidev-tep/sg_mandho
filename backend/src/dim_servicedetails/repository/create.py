from src.utils.conexion import Conexion
from src.dim_servicedetails.models.DIM_ServiceDetails import DIM_Details
def insertar_registro(data: DIM_Details) -> None:
    """
    Funcion para insertar un nuevo tipo de servicio en la base de datos
    """
    handler_coneccition = Conexion()
    query = """
    INSERT INTO DIM_ServiceDetails (
        DIM_ServiceDetailsId, 
        DIM_DateId,
        DIM_ServiceId,
        ServiceDetailesType,
        amount,
        StartDate,
        EndDate
    ) VALUES 
        ? , ? , ? , ? , ?, ?, ?
    ) """
    try:
        values = (
            data.DIM_ServiceDetailsId,
            data.DIM_DateId,
            data.DIM_ServiceId,
            data.ServiceDetailsType,
            data.amount,
            data.StartDate,
            data.EndDate
        )
        handler_coneccition.cursor.execute(query, values)
        handler_coneccition.save_changes()
    except Exception as e:  
        print(f"Error al insertar el registro: {e}")
    finally:
        handler_coneccition.close_conexion()