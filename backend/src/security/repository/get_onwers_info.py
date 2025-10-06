import sqlite3 
from src.utils.conexion import Conexion
from src.security.model import VistaModel
from src.dim_dates.dim_date import DIM_DATE

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

def get_admin_info():
    """
    Extrae la contraseña del usuario con rol 'delegado' desde la base de datos
    para el periodo de tiempo actual (año completo).

    Esta función está diseñada para obtener la credencial de un usuario específico
    ('delegado'), presumiblemente para una validación de seguridad secundaria
    o una acción crítica.

    Flujo de ejecución:
    1.  **Establecimiento de Conexión:** Inicializa una conexión a la base de datos
        a través de la clase `Conexion()`.
    2.  **Determinación de Fechas:** Utiliza una instancia de `DIM_DATE()` para
        obtener el año actual. Con este año, construye el rango de fechas
        `start_date` ("YYYY-01-01") y `end_date` ("YYYY-12-31").
    3.  **Consulta SQL:** Ejecuta una consulta SQL parametrizada contra la tabla
        `SecurityUsers`.
        -   Busca el registro donde `RoleName` sea **'delegado'**.
        -   Filtra adicionalmente por el rango de fechas (`StartDate` y `EndDate`),
            asegurando que se extraiga la información válida para el año en curso.
    4.  **Extracción de Resultado:** Llama a `hanlder_conection.cursor.fetchone()`
        para obtener el primer (y esperado único) resultado de la consulta.
    5.  **Manejo de Nulos/Ausencia de Datos:**
        -   Verifica si `user_info` es `None` (no se encontró el usuario).
        -   Verifica si el campo de la contraseña (`user_info[0]`) es `None`.
        -   En ambos casos, retorna `None`.
    6.  **Retorno:** Si se encuentra la contraseña, retorna solo el valor del campo
        `password` (`user_info[0]`).

    Manejo de Errores:
    -   Captura explícitamente `sqlite3.Error` (si la conexión o la base de datos
        es SQLite) para imprimir el error y luego relanzarlo (`raise`).

    Cierre de Recursos:
    -   Garantiza que la conexión a la base de datos se cierre siempre (`finally: hanlder_conection.close_conexion()`).

    Returns:
        str | None: La contraseña hasheada del delegado si se encuentra, o `None`
        si el usuario no existe o el campo de contraseña está vacío.
    """
    hanlder_conection = Conexion()
    
    year, month, day = DIM_DATE()._get_full_date()
    
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    query = """
    SELECT 
        password
    FROM
        SecurityUsers
    WHERE
        RoleName = 'delegado'
        AND StartDate = ?
        AND EndDate = ?
    """
    try:
        hanlder_conection.cursor.execute(query, (start_date, end_date))
        user_info = hanlder_conection.cursor.fetchone()

        # Corrección: Verificar si fetchone() devuelve None antes de acceder al índice
        if user_info is None:
            return None
        
        if user_info[0] is None:
            return None
        
        return user_info[0]
    
    except sqlite3.Error as e:
        print(f"Error al obtener la informacion del usuario: {e}")
        raise
    finally:
        hanlder_conection.close_conexion()