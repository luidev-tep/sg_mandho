import sqlite3 
from src.utils.conexion import Conexion

def update_ServiceDetails(status_id: str, DIM_ServiceDetailsId: str) -> bool:
    """
    Funcion que actualiza el unico parametro modificable de dim_service_details
    el parametro que se actualizara sera el dim_statusId, ya qi epasara no usado a usado
    
    """
    object_conetion = Conexion()
    try:
        query = """UPDATE DIM_ServiceDetails SET DIM_StatusId = ? WHERE DIM_ServiceDetailsId = ?"""
        
        valores = (status_id, DIM_ServiceDetailsId)
        object_conetion.cursor.execute(query, valores)
        object_conetion.save_changes()
        
        return True
    except sqlite3.Error as e:
        print(f"Error al actualizar el servicio: {str(e)}")
        return False
    finally:
        object_conetion.close_conexion()
        