from typing import Any, Never
from src.utils.conexion import Conexion, DatabaseError

class DIM_status:
    """
    Clase para interactuar con la tabla DIM_status en la base de datos.

    Esta clase proporciona métodos para obtener y gestionar información sobre los
    diferentes estados (activos, inactivos, pagados, etc.) que se utilizan en
    otras tablas como 'Account' o 'FactRevenue'. Su función principal es asociar
    un nombre de estado con su identificador (ID) correspondiente.
    """
    def __init__(self) -> None:
        """
        Inicializa una instancia de la clase DIM_status.

        Atributos:
            StatusName (str | None): El nombre del estado.
            StatusId (str | None): El ID del estado.
            conexion (Conexion | None): La instancia de la clase Conexion para
                                         la conexión a la base de datos.
        """
        self.StatusName = None
        self.StatusId = None
        self.conexion = None

    def get_status_id(self, StatusName: str, from_message: str) -> str:
        """
        Obtiene el ID de un estado a partir de su nombre.

        Si el nombre del estado está vacío y el mensaje de origen es 'account',
        automáticamente se asigna el estado 'activo'. Esto es útil para la
        creación de nuevas cuentas.

        Args:
            StatusName (str): El nombre del estado que se busca. Si es una
                              cadena vacía, se comporta de manera especial.
            from_message (str): Indica el origen de la solicitud ('account'
                                o 'fact_revenue') para aplicar la lógica
                                condicional.

        Returns:
            str: El ID del estado asociado si se encuentra. Retorna una cadena
                 vacía si el estado no existe en la base de datos.
        """
        self.conexion = Conexion()
        try:
            if StatusName == "" and from_message == "account":
                query = "SELECT DIM_StatusId FROM DIM_status WHERE StatusName = 'activo'"
                self.conexion.cursor.execute(query)
            else:
                query = "SELECT DIM_StatusId FROM DIM_status WHERE StatusName = ?"
                self.conexion.cursor.execute(query, (StatusName,))

            status_id = self.conexion.cursor.fetchone()

            if status_id is None:
                return ""
            return status_id[0]
        except DatabaseError as e:
            print(f"Error de base de datos al obtener el ID del estado: {e}")
            return ""
        finally:
            self.conexion.close_conexion()

    def get_status(self, id: int) -> tuple[Any, Any] | tuple[()]:
        """
        Obtiene el registro completo de un estado a partir de su ID.

        Realiza una consulta a la base de datos para encontrar el registro
        completo del estado con el ID proporcionado.

        Args:
            id (int): El ID del estado a buscar.

        Returns:
            tuple[Any, Any] | tuple[()]: Una tupla que contiene el ID y el nombre
                                         del estado si se encuentra. Retorna una
                                         tupla vacía si el registro no existe.
        """
        self.conexion = Conexion()
        try:
            query = "SELECT * FROM DIM_status WHERE DIM_StatusId = ?"
            self.conexion.cursor.execute(query, (id,))
            status = self.conexion.cursor.fetchone()

            if status:
                self.StatusId = status[0]
                self.StatusName = status[1]
                return self.StatusId, self.StatusName
            else:
                return ()
        except DatabaseError as e:
            print(f"Error de base de datos al obtener el estado: {e}")
            return ()
        finally:
            self.conexion.close_conexion()
