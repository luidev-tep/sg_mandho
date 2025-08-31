import sqlite3
from src.utils.conexion import Conexion

class EditFactRevenue:
    
    def update_many_registers(self, data_ids: list[str], column: str, value: str) -> None:
        """Esta funcion se encarga de actualizar una serie de registros ocnsecutivos, 
        de la tabl aFACT_revenue, en la base de datos.

        Args:
            data_ids (list[str]): Una lista de IDs de facturas a actualizar.
            column (str): La columna a actualizar en la base de datos.
            value (str): El nuevo valor para la columna."""
        handler_conexion = Conexion()
        # Ejemplo seguro con parámetros
        try:
            placeholders = ','.join('?' for _ in data_ids)
            query = f"UPDATE FACT_Revenue SET {column} = ? WHERE FACT_RevenueId IN ({placeholders})"
            # Preparar los valores: primero el value, luego todos los data_ids
            params = [value] + data_ids
            handler_conexion.cursor.execute(query, tuple(params))

            handler_conexion.save_changes()
        except sqlite3.Error as e:
            print(f"Error al actualizar registros: {e}")
        finally:
            handler_conexion.close_conexion()