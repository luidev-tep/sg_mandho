import sqlite3
from src.utils.conexion import Conexion
def get_pending_pays(years, DIM_accountsId, serviceName):
    try:
        handler_conexion = Conexion()
        query = f"""
            
        """
    except sqlite3.Error as e:
        print(f"Error al obtener el ID del servicio: {e}")
        return ""