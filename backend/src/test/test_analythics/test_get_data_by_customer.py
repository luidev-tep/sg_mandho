from src.analytics_reports.Analitycs import Analitycs

from src.analytics_reports.repository.PaymentProcesor import PaymentProcessor
"""
def test_get_data_by_customer():

    Prueba la función `get_analytics_per_customer` para asegurar que devuelve
    el historial de pagos de un cliente en el formato correcto.

    Escenario:
        Se proporciona un `Dim_customerId` válido.

    Resultado esperado:
        - El código de estado debe ser 200.
        - El mensaje debe ser una cadena de texto.
        - Los datos deben ser un diccionario que contenga las claves 'completos',
          'pendientes' y 'pendientes_sin_facturar'.
    
    analitycs = Analitycs()
    data_json = {
        "Dim_customerId": 'ab8c820a-8364-5860'
    }
    status, message, data = analitycs.get_analytics_per_customer(data_json)
    
    assert status == 200
    assert isinstance(message, str)
    assert isinstance(data, dict)
    assert 'completos' in data
    assert 'pendientes' in data
    assert 'pendientes_sin_facturar' in data
    
"""

def test_pending_payments():
    hanlder_ana = PaymentProcessor()
    Dim_customerId = 'ab8c820a-8364-5860'
    data = hanlder_ana.get_all_data_payments(Dim_customerId)
    assert isinstance(data, dict)
    
    