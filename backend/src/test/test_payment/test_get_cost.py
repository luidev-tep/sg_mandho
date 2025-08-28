from src.payments.payment import PaymentCrud

# def test_get_cost_service_year():
#     payment_handler = PaymentCrud()
#     data = {
#         "ServiceName": "agua", 
#         "DIM_CustomerId": "53bf0ea1-8eac-5e82"
#         }
#     code, message, response = payment_handler.get_cost(data)
#     print(message)
#     assert code == 200



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
