from src.payments.payment import PaymentCrud

def test_get_cost():
    payment_handler = PaymentCrud()
    data = {
        "service_type": "tomas", 
        "Year": 2025
        }
    code, message, response = payment_handler.get_cost_by_payment_year(data)
    print(f"code: {code}, message: {message}, response: {response}")
    assert code == 200
    assert isinstance(response, float)