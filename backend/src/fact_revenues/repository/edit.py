from src.utils.conexion import Conexion, DatabaseError

ALLOWED_COLUMNS = {"DIM_StatusId"}


class EditFactRevenue:

    def update_many_registers(
        self,
        data_ids: list[str],
        column: str,
        value: str,
        db: Conexion | None = None,
    ) -> bool:
        """Actualiza una columna permitida para múltiples registros de FACT_Revenue.

        Args:
            data_ids (list[str]): Lista de IDs de facturas (`FACT_RevenueId`) a actualizar.
            column (str): Columna a actualizar (validada contra `ALLOWED_COLUMNS`).
            value (str): Nuevo valor para la columna.
            db (Conexion | None): Conexión compartida opcional para transacciones atómicas.

        Returns:
            bool: True si la actualización fue exitosa o si `data_ids` está vacía, False en caso de error.
        """
        if not data_ids:
            return True

        if column not in ALLOWED_COLUMNS:
            return False

        handler_conexion = Conexion(shared_conn=db)
        try:
            placeholders = ','.join('?' for _ in data_ids)
            query = f"UPDATE FACT_Revenue SET {column} = ? WHERE FACT_RevenueId IN ({placeholders})"
            params = [value] + list(data_ids)
            handler_conexion.cursor.execute(query, tuple(params))

            handler_conexion.save_changes()
            return True
        except DatabaseError as e:
            print(f"Error al actualizar registros: {e}")
            return False
        finally:
            handler_conexion.close_conexion()
