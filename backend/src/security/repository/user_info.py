import sqlite3
from src.utils.conexion import Conexion

from src.security.model import VistaModel

from src.accounts.account import AccountCrud

handler_account = AccountCrud()

from src.dim_dates.dim_date import DIM_DATE

from src.dim_service.DIM_Service import DIM_Service

from src.utils.id_generator import create_id


def get_user_info(username: str, RoleName: str, manzana: str, StartDate: str, EndDate: str) -> dict[str, str] | dict:
    """
    Obtiene la información detallada de un usuario administrador específico (Owner)
    desde la vista `SecurityUsers` de la base de datos, utilizando un conjunto
    estricto de parámetros de identificación y vigencia.

    Esta función es crucial para la lógica de seguridad y administración, ya que
    permite identificar de forma única a un administrador basándose en su nombre
    de usuario, rol y el periodo exacto de su vigencia.

    La búsqueda se realiza con las siguientes condiciones (cláusula WHERE en SQL):
    - `username`: Nombre de usuario único del administrador.
    - `CustomerFraction` (manzana): La fracción o sector al que está asignado.
    - `RoleName`: El rol específico (ej. 'delegado', 'comitiva', 'subdelegado').
    - `StartDate`: Fecha de inicio de la vigencia de la cuenta.
    - `EndDate`: Fecha de fin de la vigencia de la cuenta.

    Args:
        username (str): Nombre de usuario del administrador.
        RoleName (str): Nombre del rol asignado al usuario.
        manzana (str): Fracción o manzana del usuario.
        StartDate (str): Fecha de inicio del periodo de validez de la cuenta (formato YYYY-MM-DD).
        EndDate (str): Fecha de fin del periodo de validez de la cuenta (formato YYYY-MM-DD).

    Returns:
        dict[str, str] | dict:
            - Un diccionario (`user_format`) con todos los campos del registro del usuario
              si se encuentra una coincidencia exacta.
            - `None` si no se encuentra ningún usuario que coincida con todos los criterios.

    Raises:
        sqlite3.Error: Si ocurre un error de bajo nivel durante la ejecución de la consulta
                       o la conexión a la base de datos.
    """
    handlers = Conexion()
    query = """SELECT 
            *
            FROM
                SecurityUsers 
            WHERE  username = ? AND CustomerFraction = ? AND RoleName = ? AND StartDate = ? AND EndDate = ?"""
    try:
        handlers.cursor.execute(query, (username, manzana, RoleName,  StartDate, EndDate))
        user_info = handlers.cursor.fetchone()

        if user_info is None:
            return None
        #print("User info: ", user_info)
        user_format = VistaModel(*user_info).to_dict()
        
        return user_format
    except sqlite3.Error as e:
        print(f"Error al obtener la informacion del usuario: {e}")
        raise
    finally:
        handlers.close_conexion()

def validate_user_admin() -> bool:
    """
    Verifica la regla de unicidad de los Delegados.

    Consulta la vista `SecurityUsers` para determinar si ya existe un usuario
    con el rol **'delegado'** que esté actualmente **'activo'** (`StatusName = 'activo'`).
    Dado que solo se permite **un** Delegado activo en el sistema a la vez (regla
    de negocio), esta función ayuda a prevenir la creación de múltiples cuentas
    para este rol de alto nivel.

    Returns:
        bool:
            - `True`: Si **no** existe un Delegado activo (el rol está libre para asignación).
            - `False`: Si ya existe un Delegado activo.

    Raises:
        sqlite3.Error: Propaga cualquier error que ocurra durante la conexión o la
                       ejecución de la consulta SQL.
    """
    query = """
        SELECT count( DIM_ServiceOwnersId ) active_account from SecurityUsers
        WHERE RoleName = 'delegado'
        and StatusName = 'activo';
    """
    handler_connection = Conexion()
    try:
        handler_connection.cursor.execute(query)
        result = handler_connection.cursor.fetchone()
        if result[0] == 0:
            # print("El rol activo esta libre") # Es mejor usar logging en lugar de prints
            return True
        # print("Se encontró un usuario ya con este registro")
        return False
    except sqlite3.Error as e:
        print(f"Error al verificar la informacion de la persona: {e}")
        return False
    finally:
        handler_connection.close_conexion()

def validate_user_module(module_name: str) -> bool:
    """
    Verifica la regla de unicidad para los responsables de Comitiva por Módulo/Servicio.

    Consulta la vista `SecurityUsers` para determinar si ya existe un usuario con el
    rol **'comitiva'** que esté **'activo'** para un servicio específico (`ServiceName`).
    Esto asegura que solo haya **una** persona encargada de Comitiva por cada módulo
    o servicio definido (ej. 'feria', 'panteon', 'agua').

    Args:
        module_name (str): El nombre del servicio o módulo a validar (ej. 'feria').

    Returns:
        bool:
            - `True`: Si **no** existe un Comitiva activo para el módulo dado.
            - `False`: Si ya existe un Comitiva activo para el módulo dado.

    Raises:
        sqlite3.Error: Propaga cualquier error de la base de datos.
    """
    query = """
        SELECT count( DIM_ServiceOwnersId ) active_account from SecurityUsers
        WHERE RoleName = 'comitiva'
        and StatusName = 'activo'
        AND ServiceName = ?;
    """
    handler_connection = Conexion()
    try:
        handler_connection.cursor.execute(query, (module_name,))
        result = handler_connection.cursor.fetchone()
        if result[0] == 0:
            # print("El rol activo esta libre")
            return True
        # print("Se encontró un usuario ya con este registro")
        return False
    except sqlite3.Error as e:
        print(f"Error al verificar la informacion de la persona: {e}")
        return False
    finally:
        handler_connection.close_conexion()

def validate_user_sub_admin(customerFraction: str) -> bool:
    """
    Verifica la regla de unicidad para los Subdelegados por Fracción/Manzana.

    Consulta la vista `SecurityUsers` para determinar si ya existe un usuario con el
    rol **'subdelegado'** que esté **'activo'** para una fracción de cliente específica
    (`CustomerFraction`). Esto asegura que solo haya **un** Subdelegado activo por
    manzana o sector asignado.

    Args:
        customerFraction (str): La fracción o manzana a validar.

    Returns:
        bool:
            - `True`: Si **no** existe un Subdelegado activo para la fracción dada.
            - `False`: Si ya existe un Subdelegado activo para la fracción dada.

    Raises:
        sqlite3.Error: Propaga cualquier error de la base de datos.
    """
    query = """
        SELECT count( DIM_ServiceOwnersId ) active_account from SecurityUsers
        WHERE RoleName = 'subdelegado'
        and StatusName = 'activo'
        AND CustomerFraction = ?;
    """
    handler_connection = Conexion()
    try:
        handler_connection.cursor.execute(query, (customerFraction,))
        result = handler_connection.cursor.fetchone()
        if result[0] == 0:
            # print("El rol activo esta libre")
            return True
        # print("Se encontró un usuario ya con este registro")
        return False
    except sqlite3.Error as e:
        print(f"Error al verificar la informacion de la persona: {e}")
        return False
    finally:
        handler_connection.close_conexion()

def insert_onwer_info(data: dict) -> tuple[int, str]:
    """
    Orquesta la inserción del registro de un nuevo usuario administrador (Service Owner/Propietario)
    en el sistema, realizando múltiples operaciones en una secuencia que **debería ser transaccional**
    para garantizar la atomicidad de los cambios.

    Esta función asume el rol de un controlador que realiza los siguientes pasos críticos,
    todos necesarios para que el nuevo administrador pueda operar:

    1.  **Creación de Cuenta de Servicio:**
        - Llama a `handler_account.insert_account` para crear un registro de cuenta de servicio.
          Los datos utilizados incluyen el rol (`RoleName`), el ID del cliente (`DIM_CustomerId`),
          y las fechas de vigencia (`start_date`, `end_date`), lo cual es vital para el control de acceso.

    2.  **Actualización de Credenciales del Cliente (Customer):**
        - Llama a `update_user_info` para actualizar los campos de `username` y `password`
          (ya hasheada) en la tabla maestra del cliente (`DIM_Customer`). Esto vincula las
          credenciales de acceso al registro principal del cliente.

    3.  **Registro como Propietario de Servicio (Service Owner):**
        - Llama a `insert_service_owner_info` para registrar al cliente en la tabla de
          `DIM_ServiceOwners`, detallando el servicio (`serviceName`) y el periodo de vigencia.
          Este paso otorga formalmente el cargo administrativo.

    **Nota sobre la Transacción:**
    Aunque el docstring original menciona que "se deshacen todos los cambios" en caso de falla,
    y el código simula el flujo, la función actual sólo retorna un error (`return 500, ...`).
    Para lograr un `rollback` real, las funciones internas (`insert_account`, `update_user_info`,
    `insert_service_owner_info`) deberían recibir y operar sobre el mismo objeto de conexión
    a la base de datos (como se insinúa en los comentarios del código).

    Args:
        data (dict): Diccionario que contiene todos los datos necesarios para la creación
                     del administrador: 'RoleName', 'DIM_CustomerId', 'StartDate', 'EndDate',
                     'password' (hasheada), 'username', 'serviceName', y 'CustomerFraction'.

    Returns:
        tuple[int, str]: Una tupla con el código de estado HTTP y un mensaje:
            - (200, message): Si todas las operaciones se completaron exitosamente.
            - (CÓDIGO_ERROR, message): Si falló alguna de las sub-operaciones (ej. 400, 409).
            - (500, message): Si ocurre un error de base de datos (`sqlite3.Error`) durante
                              la ejecución, indicando un fallo en la inserción.
    """
    try:
        data_for_account = {
            "status": data['RoleName'],
            "customer_id": data['DIM_CustomerId'], 
            "start_date": data["StartDate"], 
            "end_date": data["EndDate"]
        }

        estado, mensaje = handler_account.insert_account(data_for_account)
        if estado != 200:
            return estado, mensaje
        # NOTA: Se asume que `insert_account` fue modificado para aceptar un objeto de conexión
        # y no crear uno nuevo, para poder ser parte de la transacción.
        # Lo mismo para las otras funciones. Aquí se simula el flujo correcto.
        #print("Insertando propietario de servicio... Actualizar informacion del usuario...")
        #Actualizar el password y de mas en Customer
        estado, mensaje = update_user_info(data['password'], data['username'], data['DIM_CustomerId'])
        if estado != 200:
            return estado, mensaje
        
        #Ingresar al usuario en propietarios del sistema
        data_service_owner = {
            'DIM_ServiceOwnersId': create_id([data['DIM_CustomerId'], data['serviceName'], data['CustomerFraction']]),
            'DIM_CustomerId': data['DIM_CustomerId'],
            'StartDate': data['StartDate'],
            'EndDate': data['EndDate'],
            'serviceName': data['serviceName']
        }
        #print("Insertando propietario de servicio...Insetando propietario")
        response  = insert_service_owner_info(data_service_owner)
        if not response:
            return 500, "No se pudo insertar el nuevo usuario"
        
        return 200, "Usuario insertado correctamente"
    except sqlite3.Error as e:
        print(f"Error al insertar el usuario: {e}")
        return 500, "Error al insertar el usuario"

def update_user_info(password: str, username: str, dim_customer_id: str) -> tuple[int, str]:
    """
    Actualiza el nombre de usuario y la contraseña (ya hasheada) de un cliente
    específico en la tabla de dimensiones `DIM_Customer`.

    Esta función es utilizada como parte del proceso de asignación de roles
    administrativos (Owner) para otorgar credenciales de acceso al sistema
    al cliente seleccionado.

    **NOTA SOBRE TRANSACCIONES:**
    La firma de la función incluye un argumento `connection` comentado
    (aunque no utilizado en el cuerpo actual), lo que indica la intención
    de utilizar esta función dentro de una transacción mayor. Tal como está
    implementada, la función maneja su propia conexión y `commit` (`save_changes`),
    haciéndola atómica pero impidiendo un `rollback` externo si falla un paso
    posterior en el flujo de creación del administrador.

    Args:
        password (str): La nueva contraseña para el usuario (se espera que ya esté hasheada).
        username (str): El nuevo nombre de usuario único para el acceso al sistema.
        dim_customer_id (str): El identificador único del cliente a actualizar (`DIM_CustomerId`).
        connection (Conexion, optional): Conexión existente para usar en una transacción
                                         (argumento en la firma original, no usado actualmente).

    Returns:
        tuple[int, str]: Una tupla con el código de estado HTTP y un mensaje descriptivo:
            - (200, "Usuario actualizado correctamente"): Si la actualización se realizó con éxito.
            - (404, "Usuario no encontrado"): Si no se encontró ningún cliente con el `dim_customer_id` proporcionado.
            - (500, message): Si ocurre un error de bajo nivel durante la ejecución de la consulta SQL.
    """
    handler_connection = Conexion()
    try:
        query = """
            UPDATE DIM_Customer
            SET password = ?,
			username = ?
            WHERE DIM_CustomerId = ?
        """
        handler_connection.cursor.execute(query, (password, username, dim_customer_id))
        if handler_connection.cursor.rowcount == 0:
            return 404, "Usuario no encontrado"
        handler_connection.save_changes()
        return 200, "Usuario actualizado correctamente"
    except sqlite3.Error as e:
        print(f"Error al actualizar la informacion del usuario: {e}")
        return 500, "Error al actualizar la informacion del usuario"
    finally:
        handler_connection.close_conexion()

def insert_service_owner_info(data: dict) -> tuple[int, str]:
    """
    Registra un nuevo Propietario de Servicio (Service Owner) insertando un registro
    en la tabla dimensional `DIM_ServiceOwners`. Este paso formaliza la asignación
    de un rol administrativo a un cliente.

    La función obtiene automáticamente las claves foráneas necesarias antes de la inserción:
    1.  **DIM_ServiceId:** Obtenido a partir del `serviceName` proporcionado.
    2.  **DIM_DateId:** Obtenido a partir de la fecha actual a través de la clase `DIM_DATE`.

    El registro de Service Owner es esencialmente el **vínculo** entre el cliente (`DIM_CustomerId`),
    el servicio/módulo que administra (`DIM_ServiceId`), y el periodo de tiempo
    durante el cual tiene la responsabilidad (`StartDate`, `EndDate`).

    **NOTA SOBRE TRANSACCIONES:**
    Al igual que otras funciones de persistencia, esta maneja su propia conexión y `commit`.
    Para integrarla en una transacción mayor (como la creación completa de un administrador),
    se debería modificar para aceptar una conexión externa (`connection`) como se sugiere
    en la firma original, permitiendo un `rollback` si fallan otros pasos.

    Args:
        data (dict): Diccionario con la información necesaria para el registro:
                     - 'DIM_ServiceOwnersId' (str): ID único para el registro del propietario.
                     - 'DIM_CustomerId' (str): ID del cliente.
                     - 'serviceName' (str): Nombre del servicio/módulo (para obtener el ServiceId).
                     - 'StartDate' (str): Fecha de inicio de la vigencia (YYYY-MM-DD).
                     - 'EndDate' (str): Fecha de fin de la vigencia (YYYY-MM-DD).

    Returns:
        bool:
            - `True`: Si la inserción en `DIM_ServiceOwners` se completó con éxito.
            - `False`: Si ocurrió un error de base de datos (`sqlite3.Error`).
    """
    handler_connection = Conexion()
    handler = DIM_Service()
    serviceId = handler.get_service_id(data['serviceName'])
    handler_date = DIM_DATE()

    query = """
    INSERT INTO DIM_ServiceOwners (
	DIM_ServiceOwnersId,
	DIM_DateId,
	DIM_ServiceId,
	DIM_CustomerId, 
	StartDate,
	EndDate
	)
	VALUES ( 
	?,
	?,
	?,
	?,
	?,
	?)
    """
    try:
        values = (
            data['DIM_ServiceOwnersId'],
            handler_date.dateId,
            serviceId,
            data['DIM_CustomerId'],
            data['StartDate'],
            data['EndDate']
        )
        handler_connection.cursor.execute(query, values)
        handler_connection.save_changes()
        return True
    except sqlite3.Error as e:
        print(f"Error al insertar el propietario del servicio: {e}")
        return False
    finally:
        handler_connection.close_conexion()
