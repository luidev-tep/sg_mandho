from src.utils.conexion import Conexion
from src.payments.model.check_list_model import CheckListModel


def get_check_list() -> list[dict[str]] | None:
    """
    Obtiene la lista completa de clientes activos elegibles para pagos.
    
    Esta función se conecta a la base de datos y consulta la vista VISTA_CLIENTES_ACTIVOS
    para obtener todos los registros de clientes que cumplen con los criterios de elegibilidad.

    Returns:
        list[dict[str]] | None: 
            - Lista de diccionarios con la información de clientes activos en formato clave-valor
            - None: Si ocurre un error durante la consulta a la base de datos

    Note:
        Utiliza el modelo CheckListModel para transformar los resultados de la base de datos
        en diccionarios consistentes con la estructura definida en el modelo.
    """
    try:
        conn = Conexion()
        conn.cursor.execute("SELECT * FROM VISTA_CLIENTES_ACTIVOS")
        rows = conn.cursor.fetchall()
        return [CheckListModel(*row).to_dict() for row in rows]
    except Exception as e:
        print(e)
        return None
    finally:
        conn.close_conexion()
        
        
def get_status_serviceDetailes_type(year: int, service_name: str, serviceDetailes_type: str | None, from_service: str) -> str | None:
    """
    Consulta el estado de tipos de detalle de servicio para validaciones de elegibilidad.
    
    Esta función realiza consultas condicionales a la base de datos para determinar:
    - Si un tipo específico de detalle de servicio es válido para un año y servicio dado
    - Obtener todos los tipos de detalle válidos para un servicio y año específicos

    Args:
        year (int): Año de referencia para la consulta
        service_name (str): Nombre del servicio principal
        serviceDetailes_type (str | None): Tipo específico de detalle de servicio a validar.
                                          None cuando se buscan todos los tipos válidos.
        from_service (str): Contexto de llamada que determina el tipo de consulta:
                           - "is_service_valid": Validación de tipo específico
                           - "get_check_list_valids": Obtención de todos los tipos válidos

    Returns:
        str | None | list: Dependiendo del contexto:
            - Para "is_service_valid": Retorna el ID de estado (str) o None si no existe
            - Para "get_check_list_valids": Retorna lista de tuplas con (tipo, estado) o None
            - None: Si ocurre un error o no se encuentran resultados

    Note:
        La función construye consultas SQL dinámicas basadas en el parámetro 'from_service'
        y maneja automáticamente el cierre de la conexión a la base de datos.
    """
    conn = Conexion()
    query = """
        SELECT 
        [campo_adicioanl]
        DIM_StatusId
    from DIM_ServiceDetails as sv
    JOIN DIM_Service as s on 
        sv.DIM_ServiceId = s.DIM_ServiceId AND 
        s.ServiceName = ?
    JOIN DIM_Date as d on 
        d.DIM_DateId = sv.DIM_DateId 
        and d.Year = ?
    [servicio_filtro]
    """
    try:
        #print(f"los datos que llegaron: servicio {service_name}, anio {year}, tipo {serviceDetailes_type}")
        if from_service == "is_service_valid":
            print("entro a is_service_valid")
            query = query.replace("[servicio_filtro]", "WHERE ServiceDetailesType = ?")
            query = query.replace("[campo_adicioanl]", "")
        
            conn.cursor.execute(query, (service_name, year, serviceDetailes_type))
            rows = conn.cursor.fetchone()
        
        
        elif from_service == "get_check_list_valids":
            print("entro a get_check_list_valids")
            query = query.replace("[servicio_filtro]", " ")
            query = query.replace("[campo_adicioanl]", "sv.ServiceDetailesType , ")
            
            conn.cursor.execute(query, (service_name, year))
            rows = conn.cursor.fetchall()
        
        if not rows:
            return None
        if from_service == "is_service_valid":
            return rows[0]
        elif from_service == "get_check_list_valids":
            return list(rows)
    except Exception as e:
        print(e)
        return None
    finally:
        conn.close_conexion()