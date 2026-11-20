from src.utils.conexion import Conexion, DatabaseError


def get_admins_home_info() -> list:
    """
    Funcion la cual hace uan peticion a la base de de datos, esta duncion obtiene toda la ifnromacion
    de los usuarios adminstradores para mostrar en la pantalla principal.
    
    Returns:
        list: Lista de administradores con su informacion
    """
    handlers = Conexion()
    try:
        query = """
        SELECT 
            sc.fullname,
            sc.RoleName,
            CONCAT(cu.CustomerFraction, ' ', cu.CustomerAddress, ' ', cu.CustomerNumberExt) AS adress,
            sc.ServiceName
        from SecurityUsers as sc
        JOIN DIM_Customer as cu on
            sc.DIM_CustomerId  = cu.DIM_CustomerId
        """
        handlers.cursor.execute(query)
        registros = handlers.cursor.fetchall()
        data_format = []
        for registro in registros:
            persona = {
                "fullname": registro[0],
                "role_name": registro[1],
                "adress": registro[2],
                "service_name": registro[3]
            }
            data_format.append(persona)
        return data_format
    except DatabaseError as e:
        print(f"Error al realizar la consulta: {e}")
        return []
    finally:
        handlers.close_conexion()
