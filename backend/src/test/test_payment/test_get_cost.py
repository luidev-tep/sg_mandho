from src.payments.payment import PaymentCrud

from src.payments.payment import PaymentCrud


def test_get_cost_service_year():
    payment_handler = PaymentCrud()
    data = {
        "ServiceName": "panteon", 
        "DIM_CustomerId": "319e42c1-148c-552b"
        #"DIM_CustomerId": "ab8c820a-8364-5860",
        }
    code, message, response = payment_handler.get_cost(data)
    print(response)
    assert code == 200


    """
def test_get_cost_service():
    payment_handler = PaymentCrud()
    data = {
        "DIM_CustomerId": "ab8c820a-8364-5860",
        "serviceName": "agua",
        "service_type": "agua"
        }
    code, message, response = payment_handler.read_payments_customer_id(data)
    print(message)
    assert code == 200

    



def test_get_all_service_year() -> None:
    DIM_CustomerId = "319e42c1-148c-552b"
        
    response = get_all_payments_pending(DIM_CustomerId)
    for data in response:
        print(data)
        print("")
    assert isinstance(response, list)

    """