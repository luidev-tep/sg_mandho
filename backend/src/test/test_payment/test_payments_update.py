from src.payments.payment import PaymentCrud
from src.payments.repository.read_payments import ReadPayment

read_handler = ReadPayment()

payment_handler = PaymentCrud()


def test_update_payment():
    data = {
        "AnioPago": "2021",
        "DIM_AccountId": "2f5174db-0aab-5a1d",
        "DIM_CustomerId": "4ea7de6c-c997-506d",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 75.0,
        "ServiceName": "agua",
        "amount": 360.0,
        "entrada": "",
        "fecha": "2025-09-11",
        "metodoPago": "efectivo",
        "movementName": "ingreso",
        "serviceDetailsType": "consumo"
    }

    # Al tener 'entrada' vacía, create_payment internamente llamará a update_payment_view
    status_code, message, response_data = payment_handler.create_payment(data)

    print(f"Status: {status_code}, Message: {message} Response: {response_data}")

    assert status_code == 201
    assert isinstance(response_data, list)

    """

def test_read_payments():
    data = {
        "AnioPago": "2021",
        "DIM_AccountId": "2f5174db-0aab-5a1d",
        "DIM_CustomerId": "4ea7de6c-c997-506d",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 10.0,
        "ServiceName": "agua",
        "amount": 360.0,
        "entrada": "",
        "fecha": "2025-09-11",
        "metodoPago": "efectivo",
        "movementName": "ingreso",
        "serviceDetailsType": "consumo"
    }
    response_data = payment_handler.update_payment_view(data)

    print(f" Response: {response_data}")
    
    assert isinstance(response_data, list)



"""