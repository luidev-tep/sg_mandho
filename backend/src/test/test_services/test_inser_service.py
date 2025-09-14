from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud

def test_service():
    """
    Función de prueba para el método insert_service_details de la clase ServiceDetailsCrud.

    Esta función inicializa un objeto ServiceDetailsCrud, define un diccionario de datos
    de prueba para un servicio, llama al método insert_service_details con esos datos
    y luego imprime la respuesta obtenida. Finalmente, valida que la respuesta sea
    una tupla.
    """
    handler_service = ServiceDetailsCrud()
    data = {
    "serviceDetailesType": "cooperacion camino",
    "ServiceName": "panteon",
    "year": 2025,
    "amount": 200
}

    response = handler_service.insert_service_details(data)
    print(response)

    assert isinstance(response, tuple)