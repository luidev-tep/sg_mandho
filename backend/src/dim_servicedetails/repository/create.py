from src.utils.conexion import Conexion, DatabaseError
from src.dim_servicedetails.models.DIM_ServiceDetails import DIM_Details


def insertar_registro(data: DIM_Details) -> bool:
    """
    Funcion para insertar un nuevo tipo de servicio en la base de datos

    Args:
        data (DIM_Details): Objeto de la clase DIM_Details que contiene los datos del servicio a insertar.

    Returns:
        bool: True si se inserta correctamente, False en caso contrario.
    """
    object_conetion = Conexion()
    query = """
    INSERT INTO DIM_ServiceDetails (
        DIM_ServiceDetailsId,
        DIM_DateId,
        DIM_ServiceId,
        ServiceDetailesType,
        amount,
        DIM_StatusId,
        StartDate,
        EndDate
    ) VALUES (
        ? , ? , ? , ? , ?, ?, ?, ?
    ) """
    try:
        values = (
            data.DIM_ServiceDetailsId,
            data.DIM_DateId,
            data.DIM_ServiceId,
            data.serviceDetailesType,
            data.amount,
            data.isOptional,
            data.StartDate,
            data.EndDate,
        )
        object_conetion.cursor.execute(query, values)
        object_conetion.save_changes()
        return True
    except DatabaseError as e:
        print(f"Error al insertar el registro: {e}")
        return False
    finally:
        object_conetion.close_conexion()
