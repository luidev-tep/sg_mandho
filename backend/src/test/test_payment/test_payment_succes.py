from src.payments.payment import PaymentCrud
import datetime
import pytest

@pytest.fixture
def payment_handler():
    return PaymentCrud()

'''Id esperado para el ususari
cb7d41e5-344a-577b

319e42c1-148c-552b
'''

@pytest.fixture
def valid_payment_data() -> dict[str, str | float | int]:
    """Datos de pago válidos para usar como base en los tests"""
    return {
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "DIM_AccountId": "6c74ce4a-53b7-5c66",
        "DIM_CustomerId": "319e42c1-148c-552b",
        "ServiceName": "agua",
        "serviceDetailsType": "tomas",
        "amount": 360.0,
        "AnioPago": 2025,
        "FactAmount": 50.0,
        "movementName": "ingreso",
        "StartDate": "2022-01-01",
        "EndDate": "2022-12-31",
        "entrada": ''
    }

def test_partial_data_success(payment_handler: PaymentCrud, valid_payment_data):
    """
    Test que campos adicionales no requeridos no afectan el funcionamiento:
    1. Verifica que con datos adicionales (no requeridos) se crea correctamente
    2. Si falla, verifica que el error sea por otra razón (no por los campos extra)
    """
    status_code, message = payment_handler.create_payment(valid_payment_data)
    
    print(f"Mensaje: {message} , Estado: {status_code}")
    if status_code != 201:
        # Si falla, verificar que el error NO sea por los campos adicionales
        pytest.fail(f"Falló por otra razón: {message} (código {status_code})")
    else:
        assert status_code == 201
        assert message == "Pago creado satisfactoriamente"