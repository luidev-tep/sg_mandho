import sqlite3 
from src.utils.conexion import Conexion
from src.security.model import VistaModel

def get_securyty_users_info():
    """
    Recupera la lista completa de todos los usuarios administradores (Propietarios/Owners)
    activos e inactivos del sistema consultando la vista `SecurityUsers`.

    Esta función está diseñada para ser utilizada en interfaces de administración
    (como la tabla de visualización de administradores activos) donde se requiere
    mostrar una lista completa de quién ostenta o ha ostentado un cargo administrativo.

    ### Proceso de Extracción y Filtrado:

    1.  **Consulta:** Ejecuta una consulta `SELECT *` sobre la vista `SecurityUsers` para
        obtener todos los campos de cada registro.
    2.  **Mapeo:** Cada fila de la base de datos se mapea a una instancia de `VistaModel`
        y luego se convierte a un diccionario.
    3.  **Seguridad y Limpieza:** El resultado final se limpia para **excluir campos sensibles**
        o internos antes de ser devuelto. Los campos excluidos son:
        -   `password`
        -   `username`
        -   `DIM_CustomerId` (ID maestro del cliente)
        -   `DIM_ServiceOwnersId` (ID interno del registro de propietario)
        -   `DIM_AccountId` (ID de la cuenta de seguridad)

    Returns:
        list[dict] | None:
            - Una lista de diccionarios, donde cada diccionario representa un usuario
              administrador con la información limpia y visible (nombre, rol, servicio,
              vigencia, estado).
            - `None` si la base de datos retorna un conjunto de resultados vacío.

    Raises:
        sqlite3.Error: Si ocurre un error durante la conexión o la ejecución de la consulta.
                       El error se imprime y luego se propaga.
    """
    hanlder_conection = Conexion()
    query = """
    SELECT 
            *
    FROM
        SecurityUsers
    """
    try:
        hanlder_conection.cursor.execute(query)
        user_info = hanlder_conection.cursor.fetchall()

        if user_info is None:
            return None
        
        data = [VistaModel(*user).to_dict() for user in user_info]
        
        excluded_fields = {"password", "username", "DIM_CustomerId", "DIM_ServiceOwnersId", "DIM_AccountId"}
        # print('Data curda')
        # print(data)
        list_data = []
        for item in data:
            data_onwers_info_format = {
                key: value for key, value in item.items() 
                if key not in excluded_fields
            }
            list_data.append(data_onwers_info_format)
        
        return list_data
    except sqlite3.Error as e:
        print(f"Error al obtener la informacion del usuario: {e}")
        raise
    finally:
        hanlder_conection.close_conexion()