from src.payments.repository.get_check_list import get_status_serviceDetailes_type


def is_service_valid(year: int, service_name: str, service_type: str):
    """
    Verifica si un servicio es válido para un año específico según su estado.
    
    Esta función consulta el estado del servicio para determinar si está habilitado
    para el año solicitado, utilizando el módulo de gestión de checklist.

    Args:
        year (int): Año de referencia para la validación del servicio
        service_name (str): Nombre identificador del servicio a validar
        service_type (str): Tipo o categoría del servicio

    Returns:
        bool: 
            - True: El servicio está disponible y válido para el año especificado
            - False: El servicio no está disponible o ocurrió un error en la validación

    Note:
        Maneja excepciones internamente y retorna False en caso de error para
        evitar interrupciones en el flujo principal de la aplicación.
    """
    try:
        #print(f"los datos que llegaron: servicio {service_name}, anio {year}, tipo {service_type}")
        chek_list_status = get_status_serviceDetailes_type(year, service_name, service_type, "is_service_valid")
        #print(f"chek_list_status: {chek_list_status}")
        if chek_list_status is None:
            return False
        
        return obtener_status(chek_list_status)
        
    except Exception as e:
        print(e)
        return False
    
def get_check_list_valids(year: int, service_name: str):
    """
    Obtiene la lista de tipos de servicio válidos para un año y servicio específicos.
    
    Consulta todos los tipos de servicio asociados a un servicio principal y año,
    filtrando solo aquellos que tienen un estado válido según las reglas de negocio.

    Args:
        year (int): Año de referencia para la consulta
        service_name (str): Nombre del servicio principal para el cual se buscan tipos válidos

    Returns:
        list: Lista de strings con los nombres de los tipos de servicio válidos.
              Retorna lista vacía si no hay tipos válidos o ocurre un error.

    Example:
        >>> get_check_list_valids(2024, "ServicioA")
        ['tipo1', 'tipo2', 'tipo3']
    """
    try:
        
        servicedatyles_valids = get_status_serviceDetailes_type(year, service_name, None, "get_check_list_valids")
        
        if servicedatyles_valids is None:
            return []
        
        servicios_validos = [servicio[0] for servicio in servicedatyles_valids if obtener_status(servicio[1])]
        #Verifica si la tabla se puede utilizar
        
        return servicios_validos
    except Exception as e:
        print(e)
        return []
    
def obtener_status(id_estatus: str):
    """
    Determina el estado de validez basado en el identificador de estatus.
    
    Función auxiliar que implementa la lógica de negocio para convertir códigos
    de estatus en valores booleanos que indican validez.

    Args:
        id_estatus (str): Identificador del estatus a evaluar (ej: 'status7', 'status6')

    Returns:
        bool: 
            - True: El estatus indica que el elemento es válido (solo para 'status7')
            - False: El estatus indica que el elemento no es válido o el código no coincide

    Note:
        Actualmente solo 'status7' es considerado como estado válido. Esta lógica
        puede extenderse para soportar más códigos de estatus en el futuro.
    """
    #Verifica si la tabla se puede utilizar
    if id_estatus == 'status7':
        return True
    
    return False