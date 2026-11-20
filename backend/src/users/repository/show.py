from src.utils.conexion import Conexion, DatabaseError
from src.users.models.user import User
from src.utils.build_filters import BuildFilters


#POR EL MOMENTO SE CREE QUE ESTA FUNCION YA NO ES FUNCIONAL.
#SE PRETENDE ELIMINARLA DE SER ASI
def get_all_users() -> list:
    """Funcion la cual sirve para obtener a todos los usuarios, 
    se usa cuando tanto los filtros como la id_user estan vacios
    Args:
        None
    Returns:
        list: Todos los registros que se encuentren en la base de datos
    """
    handlers = Conexion()
    try:
        conn, cursor = handlers.conexion()
        query = """SELECT * FROM DIM_Customer"""
        cursor.execute(query)
        registros = cursor.fetchall()
        
        data_format = []
        #Registros mapeados a como deben de llamarse en el frontend
        for registro in registros:
            #Mapeado a como se enviaran en el frontend
            persona = {
                "id_user": registro[0],
                "date_id": registro[1],
                "first_name": registro[2],
                "second_name": registro[3],
                "last_name": registro[4],
                "second_last_name": registro[5],
                "date_of_birth": registro[6],
                "date_user_start": registro[7],
                "date_user_end": registro[8],
                "manzana": registro[9],
                "street": registro[10],
                "number_ext": registro[11]
            }
            data_format.append(persona)
        print("desde show en users")
        return data_format
    finally:
        handlers.close_conexion()
    
def get_user(id_user: str) -> dict[str, str] | dict:
    """
    Funcion para optener la informacion de un usuario en especifico
    Args:
        id_user (str, optional): Id del usuario. Defaults to None.
    Returns:
        list: Con el registro encontrado o error en caso contrario
    """

    print(f"Id de usuario: {id_user}")

    handlers = Conexion() 

    try:
        # Se instancia la clase para todas las funciones  
        conn, cursor = handlers.conexion()

        # Usando parámetros seguros para evitar SQL injection
        query = """SELECT  
        DIM_CustomerId,
        DIM_DateId,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        CustomerDateBirth,
        CustomerStartDate,
        CustomerEndDate,
        CustomerFraction,    
        CustomerAddress,
        CustomerNumberext
        FROM DIM_Customer WHERE DIM_CustomerId = ?"""
        cursor.execute(query, (id_user,))

        registros = cursor.fetchall()

        if registros:  # Si se encontraron resultados
            # Tomamos el primer registro (asumiendo búsqueda por ID devuelve solo 1)
            primer_registro = registros[0]
            
            # Mapeo manual de la tupla a los parámetros de User
            # IMPORTANTE: Asegúrate que el orden de las columnas coincide con tu SELECT *
            registro = User(*primer_registro)
            return registro.to_dict()  # Devuelve el objeto User directamente
        else:
            return {}  # O puedes lanzar una excepción si lo prefieres
    
    except DatabaseError as e:
        print(f"Error al realizar la consulta: {e}")
        return {}
    finally:
        handlers.close_conexion()


def get_users_with_filters(filters: dict[str, str]) -> list[dict[str, str]] | list:
    """
    Obtiene información de usuarios aplicando filtros especificados.
    
    Args:
        filters (dict[str, str]): Diccionario con los filtros a aplicar.
            - CustomerFraction: Lista de manzanas a filtrar
            - CustomerEndDate: Fecha de fin opcional
            - DIM_Date: Filtros de fecha fiscal
            
    Returns:
        list[dict]: Lista de usuarios que coinciden con los filtros
    """
    conecion = Conexion()
    handler_filters = BuildFilters()
    # Query base - Asegurando que coincida el número de columnas seleccionadas con las esperadas
    query = """SELECT       
        p.DIM_CustomerId,
        p.CustomerName,
        p.CustomerMiddleName,
        p.CustomerLastName,
        p.CustomerSecondLastName,
        p.CustomerDateBirth,
        p.CustomerStartDate,
        p.CustomerEndDate,
        p.CustomerFraction,
        p.CustomerAddress,
        p.CustomerNumberExt
     FROM DIM_Customer AS p
     INNER JOIN DIM_Date AS d ON p.DIM_DateId = d.DIM_DateId
     WHERE 1 = 1 """

    valores = []
    
    try:
        if 'moduloPago' in filters and filters['moduloPago']:
            #query += f" AND "
            pass

        # Construcción de condiciones (se mantiene igual)
        if 'CustomerFraction' in filters and filters['CustomerFraction']:
            manzana_cond, manzana_values = handler_filters.build_manzana_condition(filters['CustomerFraction'])
            if manzana_cond:
                query += f" AND ({manzana_cond})"
                valores.extend(manzana_values)

        if 'CustomerEndDate' in filters and filters['CustomerEndDate']:
            query += " AND  p.CustomerEndDate <> 's/n'"

        fechas_cond, fechas_values = handler_filters.add_date(filters.get("DIM_Date"))
        if fechas_cond:
            query += f" AND {fechas_cond}"
            valores.extend(fechas_values)
        #print("[DEBUG] Query generado:", query)
        #print("[DEBUG] Valores:", valores)
        conecion.cursor.execute(query, tuple(valores))
        registros = conecion.cursor.fetchall()
        data_format = []
        
        for registro in registros:
            # Mapeo seguro basado en el número real de columnas
            persona = {
                "id_user": registro[0],
                "first_name": registro[1],
                "second_name": registro[2],
                "last_name": registro[3],
                "second_last_name": registro[4],
                "date_of_birth": registro[5],
                "date_user_start": registro[6],
                "date_user_end": registro[7],
                "manzana": registro[8],
                "street": registro[9],
                "number_ext": registro[10] if len(registro) > 10 else None
            }
            
            data_format.append(persona)

        #print(f" Se encontraron {len(data_format)} registros")
        return data_format

    except Exception as e:
        print(f"[ERROR] Fallo al ejecutar consulta: {str(e)}")
        raise
    finally:
        conecion.close_conexion()


def get_user_register_creation(dim_customer_id: str) -> str | None:
    """
    Funcion para optener la informacion de un usuario en especifico
    Args:
        id_user (str, optional): Id del usuario. Defaults to None.
    Returns:
        list: Con el registro encontrado o error en caso contrario
    """

    #print(f"Id de usuario: {dim_customer_id}")
    object_conection = Conexion() 
    
    try:
        query = """SELECT CustomerStartDate FROM DIM_Customer WHERE DIM_CustomerId = ?"""
        object_conection.cursor.execute(query, (dim_customer_id,))
        registros = object_conection.cursor.fetchone()
        
        if registros is not None:
            print(f'se retorna el anio que se consiguio {registros}')
            return registros[0]
        else:
            return None
    except DatabaseError as e:
        print(f"Error al realizar la consulta: {e}")
    finally:
        object_conection.close_conexion()
