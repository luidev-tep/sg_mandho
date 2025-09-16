from src.payments.payment import PaymentCrud

payment_handler = PaymentCrud()

from src.payments.services.check_list_services import get_check_list_valids

def test_get_check_list():
    """
    Test unitario para verificar la funcionalidad de obtención de lista de check list válidos.
    
    Este test valida que la función get_check_list_valids retorne una lista con los check list
    correspondientes al año y servicio especificado.
    
    Pruebas realizadas:
    - Verifica que el tipo de dato retornado sea una lista
    - Valida la respuesta con parámetros específicos de año y nombre de servicio
    
    Args:
        None
        
    Returns:
        None
        
    Raises:
        AssertionError: Si la respuesta no es del tipo lista esperado
        
    Example:
        >>> test_get_check_list()
        response: [{'id': 1, 'name': 'Checklist 1'}, {'id': 2, 'name': 'Checklist 2'}]
    """
    year = '2025'
    service_name = "panteon"
    service_type = "faena"
    response = get_check_list_valids(year, service_name)
    print(f"response: {response}")
    assert isinstance(response, list)