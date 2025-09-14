from src.dim_servicedetails.repository.show import get_similar_services

def valide_service_details(service_details_json: dict) -> bool:
    """
    Funcion la cual se encarga de validar que no haya un servicio similar en el año ingresado 
    el cual es el actual, ya que no se pueden crear servicios futuros
    """
    # se obtiene la informacion correcta para que se hagan las consultas
    year = str(service_details_json['year'])
    year = year[2:]
    year = f'Y{year}'

    return get_similar_services(service_details_json['ServiceName'], year, service_details_json['serviceDetailesType'])
    

