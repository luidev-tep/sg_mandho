from src.payments.repository.get_pending_pays import get_pending_pays
from src.payments.payment import PaymentCrud


def test_get_cost_service_year():
    payment_handler = PaymentCrud()
    data = {
        "ServiceName": "panteon", 
        "DIM_CustomerId": "0d6bff58-7aa2-5d23"
        #"DIM_CustomerId": "ab8c820a-8364-5860",
        }
    code, message, response = payment_handler.get_pending_paids_per_customer(data)
    print(message)
    print(response)
    assert code == 200

# def test_get_cost_individual():
#     payment_handler = PaymentCrud()
#     # data = {
#     #     "ServiceName": "panteon", 
#     #     "DIM_CustomerId": "0d6bff58-7aa2-5d23"
#     #     #"DIM_CustomerId": "ab8c820a-8364-5860",
#     #     }
#     ServiceName = "panteon"
#     DIM_CustomerId = "0d6bff58-7aa2-5d23"
#     data = get_pending_pays(DIM_CustomerId, ServiceName)
#     print(data  )
#     assert isinstance(data, list)
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
    assert code == 200 get_pending_pays

    



def test_get_all_service_year() -> None:
    DIM_CustomerId = "319e42c1-148c-552b"
        
    response = get_all_payments_pending(DIM_CustomerId)
    for data in response:
        print(data)
        print("")
    assert isinstance(response, list)

    """